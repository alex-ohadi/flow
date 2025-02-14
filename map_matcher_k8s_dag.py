from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_job import KubernetesJobOperator
from datetime import datetime

# Define DAG default arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

# Define DAG
dag = DAG(
    "map_matcher_k8s",  # DAG ID
    default_args=default_args,
    schedule_interval="0 12 * * *",
    catchup=False,
)

# Define Kubernetes Job Task
run_k8s_job = KubernetesJobOperator(
    task_id="run_map_matcher",
    namespace="default",  # Update if using a different namespace
    generate_name="map-matcher-",  # Auto-generates unique job names
    in_cluster=True,  # Set to False if Airflow runs outside the cluster
    config_file=None,  # Only needed if running Airflow outside K8s
    dag=dag,
)

run_k8s_job
