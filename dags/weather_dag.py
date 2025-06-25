"""
DAG to collect weather data and store it in Scaleway Object Storage
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from src.data_pipeline.ingestion.weather_data_collector import main

default_args = {
    'owner': 'weather_etl',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False,
}


with DAG(
        'weather_data_collection',
        default_args=default_args,
        description='Collects weather data from API and stores in Scaleway Object Storage',
        start_date=datetime.now() - timedelta(days=1),
        catchup=False,
        tags={'weather', 'data_collection', 'ETL'},
) as dag:

    # Use PythonOperator to run the weather data collection
    collect_weather_task = PythonOperator(
        task_id='collect_weather_data',
        python_callable=main,
    )

    # Use BashOperator to run dbt build command
    # Could also use: https://pypi.org/project/airflow-dbt-python/
    transform_weather_task = BashOperator(
        task_id='transform_weather_data',
        bash_command='cd /opt/airflow/app/dbt && dbt build',
        retries=2,
        retry_delay=timedelta(minutes=2),
    )

    # Set task dependencies
    collect_weather_task >> transform_weather_task