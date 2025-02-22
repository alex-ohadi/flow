import os
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import V1VolumeMount, V1Volume
from datetime import datetime

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

# Define DAG
dag = DAG(
    "map_matcher_k8s", 
    default_args=default_args,
    schedule="0 12 * * *",  # Run daily at 12:00 UTC
    catchup=False,
)

# Define the volume for the job directory
volume = V1Volume(
    name="dags-volume",
    host_path={"path": "/mnt/data", "type": "Directory"}  # Corrected path inside Minikube
)
# Define the volume mount for the job directory inside the pod
volume_mount = V1VolumeMount(
    mount_path="/opt/airflow/dags/k8s/jobs",  # Path in the pod where the job will be mounted
    name="dags-volume",  # The name of the volume
    read_only=False  # Allow write access if needed (set this to True if no writing is needed)
)

# Define KubernetesPodOperator to delete the job using kubectl
delete_job_task = KubernetesPodOperator(
    task_id="delete_map_matcher_job",
    name="delete-map-matcher-job",
    namespace="flow-alex",  # Specify your namespace
    image="bitnami/kubectl",  # Image with kubectl installed
    cmds=["kubectl", "delete", "job", "map-matcher"],
    is_delete_operator_pod=True,
    get_logs=True,
    volumes=[volume],  # Use the volume here
    volume_mounts=[volume_mount],  # Use the volume mount here
    dag=dag,
)

# Define KubernetesPodOperator to create the job using kubectl
create_job_task = KubernetesPodOperator(
    task_id="create_map_matcher_job",
    name="create-map-matcher-job",
    namespace="flow-alex",  # Specify your namespace
    image="bitnami/kubectl",  # Image with kubectl installed
    cmds=["kubectl", "create", "-f", "/opt/airflow/dags/k8s/jobs/map-matcher-job.yml"],
    is_delete_operator_pod=True,
    get_logs=True,
    volumes=[volume],  # Use the volume here
    volume_mounts=[volume_mount],  # Use the volume mount here
    dag=dag,
)

# Task dependencies: delete job first, then create it
delete_job_task >> create_job_task
