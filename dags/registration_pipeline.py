"""
Airflow DAG that orchestrates the EU vehicle registration ETL pipeline monthly.

Copy this file into your Airflow $AIRFLOW_HOME/dags folder, or map it via
Docker Compose volumes.
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from extract import main as extract_main
from transform import main as transform_main
from load import main as load_main

default_args = {
    "owner": "portfolio",
    "retries": 2,
}

with DAG(
    dag_id="eu_vehicle_registration_etl",
    description="Ingere, transforma e carrega dados de registro de veículos na UE (Eurostat).",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@monthly",
    catchup=False,
    default_args=default_args,
    tags=["automotive", "portfolio", "etl"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract_main,
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform_main,
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load_main,
    )

    extract_task >> transform_task >> load_task
