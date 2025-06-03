from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import redis
import psycopg2
import json
import os

# Configs — replace these if using Airflow Variables/Secrets
REDIS_HOST = 'redis'
REDIS_PORT = os.getenv('REDIS_HOST', "host.docker.internal")

PG_HOST = 'timescaledb'
PG_PORT = 5432
PG_USER = 'joeynguyen'
PG_PASSWORD = 'joeynguyen'
PG_DB = 'binance-api'

# The Redis key(s) where Binance price data is stored
REDIS_KEY = 'agg_trade:*'

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def transfer_data(**context):
    # Connect to Redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    # Connect to TimescaleDB
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )
    cursor = conn.cursor()

    # Read all data from Redis hash
    data = r.hgetall(REDIS_KEY)