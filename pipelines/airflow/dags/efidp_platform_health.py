"""
EFIDP Platform Health Validation DAG.
Phase 2 only: verifies that Airflow can connect to the DAG store and scheduler is operational.
No business logic is implemented here — this is a minimal connectivity smoke-test.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


def platform_health_check() -> None:
    """Log Airflow platform health confirmation."""
    import logging

    logging.getLogger(__name__).info("EFIDP Airflow scheduler is healthy and reachable.")


with DAG(
    dag_id="efidp_platform_health",
    description="Phase 2 smoke-test: validates Airflow scheduler and DAG loading.",
    schedule=timedelta(hours=24),
    start_date=datetime(2026, 9, 24),
    catchup=False,
    tags=["efidp", "infrastructure", "phase-2"],
) as dag:
    health_task = PythonOperator(
        task_id="platform_health_check",
        python_callable=platform_health_check,
    )
