"""Daily Olist e-commerce analytics pipeline.

ingest (Python -> Postgres raw)  >>  dbt deps  >>  dbt run  >>  dbt test
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

DBT_PROJECT_DIR = os.environ.get("DBT_PROJECT_DIR", "/opt/ecommerce/dbt")
DBT_PROFILES_DIR = os.environ.get("DBT_PROFILES_DIR", DBT_PROJECT_DIR)
INGEST_PATH = os.environ.get("ECOMMERCE_INGEST_PATH", "/opt/ecommerce/src/ingest.py")

DEFAULT_ARGS = {
    "owner": "sri-charan",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def run_ingest() -> None:
    import importlib.util
    from pathlib import Path

    path = Path(INGEST_PATH)
    spec = importlib.util.spec_from_file_location("ecommerce_ingest", path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Cannot load ingest script at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rc = module.main()
    if rc != 0:
        raise RuntimeError(f"Ingest exited with {rc}")


with DAG(
    dag_id="ecommerce_analytics_pipeline",
    description="Ingest the Olist e-commerce extract into Postgres, then build and test dbt marts.",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 11, 1),
    schedule="0 6 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["ecommerce", "olist", "dbt", "postgres"],
) as dag:
    ingest_olist = PythonOperator(
        task_id="ingest_olist",
        python_callable=run_ingest,
    )

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=(
            "dbt deps "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "dbt run "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} "
            "--target dev"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "dbt test "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} "
            "--target dev"
        ),
    )

    ingest_olist >> dbt_deps >> dbt_run >> dbt_test
