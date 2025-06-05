from datetime import datetime, timedelta
import redis
import psycopg2
import os

# Configs — replace these if using Airflow Variables/Secrets
# REDIS_HOST = os.getenv('REDIS_HOST', 'host.docker.internal' if os.getenv('IN_DOCKER') else 'localhost')
REDIS_HOST = 'host.docker.internal'
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

PG_HOST = 'timescaledb'
PG_PORT = '5432'
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
def agg_trade_ensure_table_exists(conn):
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

def mark_price_ensure_table_exists(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mark_price (
            id SERIAL PRIMARY KEY,
            event_type TEXT,
            event_time TIMESTAMPTZ,
            symbol TEXT,
            mark_price DOUBLE PRECISION,
            estimated_settle_price DOUBLE PRECISION,
            index_price DOUBLE PRECISION,
            funding_rate DOUBLE PRECISION,
            next_funding_time TIMESTAMPTZ
        );
    """)
    conn.commit()
    cursor.close()

def agg_trade_transfer_data(**context):
    # Connect to Redis
    r = connect_redis()
    # Connect to TimescaleDB
    conn = connect_pg()
    agg_trade_ensure_table_exists(conn)
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

def mark_price_transfer_data(**context):
    # Connect to Redis
    r = connect_redis()

    # Connect to TimescaleDB
    conn = connect_pg()
    mark_price_ensure_table_exists(conn)
    cursor = conn.cursor()

    # Get all mark price keys
    keys = r.keys('!markPrice@arr:*')
    
    for key in keys:
        data = r.hgetall(key)
        if not data:
            continue
        print(data)

        try:
            event_type = data.get('Event type')
            event_time = datetime.fromtimestamp(int(data.get('Event time', '0')) / 1000) if data.get('Event time') else None
            symbol = data.get('Symbol')
            mark_price = float(data.get('Mark price')) if data.get('Mark price') else None
            estimated_settle_price = float(data.get('Estimated Settle Price')) if data.get('Estimated Settle Price') else None
            index_price = float(data.get('Index price')) if data.get('Index price') else None
            funding_rate = float(data.get('Funding rate')) if data.get('Funding rate') else None
            next_funding_time = datetime.fromtimestamp(int(data.get('Next funding time', '0')) / 1000) if data.get('Next funding time') else None

            cursor.execute("""
                INSERT INTO mark_price (
                    event_type, event_time, symbol,
                    mark_price, estimated_settle_price,
                    index_price, funding_rate, next_funding_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                event_type, event_time, symbol,
                mark_price, estimated_settle_price,
                index_price, funding_rate, next_funding_time
            ))
            r.delete(key)

        except Exception as e:
            print(f"Error inserting key {key}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

def mark_price_transfer_data_latest(**context):
    # Connect to Redis
    r = connect_redis()

    # Connect to TimescaleDB
    conn = connect_pg()
    cursor = conn.cursor()
    cursor.execute("""
                    DROP TABLE IF EXISTS mark_price_latest;
                   
                    CREATE TABLE mark_price_latest AS
                    WITH latest_price AS (
                        SELECT symbol, MAX(event_time)
                        FROM mark_price
                        GROUP BY symbol)
                    SELECT mark_price.* FROM mark_price
                    LEFT JOIN latest_price on mark_price.symbol = latest_price.symbol
                    WHERE event_time = max;""")
    conn.commit()
    cursor.close()
    conn.close()