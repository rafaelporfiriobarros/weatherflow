"""Orquestracao do pipeline WeatherFlow."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/project"

with DAG(
    dag_id="weatherflow_daily",
    description="Pipeline diario de previsoes meteorologicas",
    start_date=datetime(2026, 11, 1),
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "weatherflow",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["weatherflow", "engenharia-de-dados"],
) as dag:
    extract_weather = BashOperator(
        task_id="extract_weather",
        bash_command=(f"cd {PROJECT_DIR} && python -m weatherflow.main"),
    )

    load_weather = BashOperator(
        task_id="load_weather",
        bash_command=(f"cd {PROJECT_DIR} && python -m weatherflow.etl"),
    )

    extract_weather >> load_weather
