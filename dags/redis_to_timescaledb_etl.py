from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from binanceapi_etl import redis_to_timescaledb  # your module should expose both functions

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='redis_to_timescaledb_etl_dag',
    default_args=default_args,
    description='Run agg_trade and mark_price ETL every 5 minutes',
    schedule_interval='*/5 * * * *',
    start_date=datetime(2025, 6, 1),
    catchup=False,
    tags=['binance', 'etl']
) as dag:

    # Task 1: Transfer agg_trade data
    run_agg_trade_etl = PythonOperator(
        task_id='run_agg_trade_etl',
        python_callable=redis_to_timescaledb.agg_trade_transfer_data
    )
    # Task 2: Transfer mark_price data
    run_mark_price_etl = PythonOperator(
        task_id='run_mark_price_etl',
        python_callable=redis_to_timescaledb.mark_price_transfer_data  # Assuming it's defined in the same module
    )
    # Task 3: Create a new table (replace if exists) showing the latest mark_prices
    run_mark_price_latest_etl = PythonOperator(
    task_id='run_mark_price_latest_etl',
    python_callable=redis_to_timescaledb.mark_price_transfer_data_latest  # Assuming it's defined in the same module
    )
    # Task 1, Task 2 run, then Task 3
    [run_agg_trade_etl, run_mark_price_etl] >> run_mark_price_latest_etl
