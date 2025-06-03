from datetime import datetime, timedelta
import redis
import psycopg2
import json
import os
import time

# Configs — replace these if using Airflow Variables/Secrets
REDIS_HOST = os.getenv('REDIS_HOST', 'host.docker.internal' if os.getenv('IN_DOCKER') else 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# PG_HOST = 'timescaledb'
PG_HOST = 'localhost'
PG_PORT = 5432
PG_USER = 'joeynguyen'
PG_PASSWORD = 'joeynguyen'
PG_DB = 'binance-api'

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}
def parse_bool(value):
    return value.lower() in ['true', '1', 'yes'] if isinstance(value, str) else bool(value)
def connect_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
def connect_pg():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )
def ensure_table_exists(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agg_trade (
            id SERIAL PRIMARY KEY,
            event_type TEXT,
            event_time TIMESTAMPTZ,
            agg_trade_id BIGINT,
            symbol TEXT,
            price DOUBLE PRECISION,
            quantity DOUBLE PRECISION,
            first_trade_id BIGINT,
            last_trade_id BIGINT,
            is_buyer_market_maker BOOLEAN,
            stream TEXT,
            trade_time TIMESTAMPTZ
        );
    """)
    conn.commit()
    cursor.close()

def transfer_data(**context):
    # Connect to Redis
    r = connect_redis()
    # Connect to TimescaleDB
    conn = connect_pg()
    ensure_table_exists(conn)
    cursor = conn.cursor()

    # The Redis key(s) where Binance price data is stored
    keys = r.keys('agg_trade:*')
    # Read all data from Redis hash
    for key in keys:
        data = r.hgetall(key)
        if data:
            print(data)
        else:
            continue
        
        try:
            event_type = data.get('Event type')
            event_time = datetime.fromtimestamp(int(data.get('Event time', '0')) / 1000) if data.get('Event time') else None
            agg_trade_id = int(data.get('Aggregate trade ID')) if data.get('Aggregate trade ID') else None
            symbol = data.get('Symbol')
            price = float(data.get('Price')) if data.get('Price') else None
            quantity = float(data.get('Quantity')) if data.get('Quantity') else None
            first_trade_id = int(data.get('First trade ID')) if data.get('First trade ID') else None
            last_trade_id = int(data.get('Last trade ID')) if data.get('Last trade ID') else None
            is_buyer_market_maker = parse_bool(data.get('Is the buyer the market maker?'))
            stream = data.get('stream')
            trade_time = datetime.fromtimestamp(int(data.get('Trade time', '0')) / 1000) if data.get('Trade time') else None

            cursor.execute("""
                INSERT INTO agg_trade (
                    event_type, event_time, agg_trade_id, symbol,
                    price, quantity, first_trade_id, last_trade_id,
                    is_buyer_market_maker, stream, trade_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                event_type, event_time, agg_trade_id, symbol,
                price, quantity, first_trade_id, last_trade_id,
                is_buyer_market_maker, stream, trade_time
            ))
            r.delete(key)
        except Exception as e:
            print(f"Error inserting key {key}: {e}")
    conn.commit()
    cursor.close()
    conn.close()
transfer_data()


# if __name__ == "__main__":
#     while True:
#         print(f"[{datetime.now()}] Checking Redis for new data...")
#         try:
#             transfer_data()
#         except Exception as e:
#             print("Fatal error:", e)
#         time.sleep(300)  # sleep 5 minutes