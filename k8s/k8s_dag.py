from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

def run_k8s_job():
    # Delete the existing job if it exists
    subprocess.run(["kubectl", "delete", "job", "map-matcher"], check=False)
    
    # Now create the job again
    subprocess.run(["kubectl", "create", "-f", "./k8s/jobs/map-matcher.yaml"], check=True)

# Define DAG
dag = DAG(
    "map_matcher_k8s", 
    default_args=default_args,
    schedule="0 12 * * *",  # Run daily at 12:00 UTC
    catchup=False,
)

# Define Python task to run the map matcher job
run_k8s_job_task = PythonOperator(
    task_id="run_map_matcher",
    python_callable=run_k8s_job,
    dag=dag,
)

run_k8s_job_task
