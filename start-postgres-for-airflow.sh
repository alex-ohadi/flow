#!/bin/bash

set -e

echo "** Starting airflow deployment **"

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo "Minikube is not running. Please start Minikube first."
    exit 1
fi

# Ensure the namespace exists
kubectl get namespace $NAMESPACE || kubectl create namespace $NAMESPACE

# Add the Airflow Helm repository
helm repo add airflow-stable https://airflow-helm.github.io/charts
helm repo update

# Variables
RELEASE_NAME=my-airflow-cluster
NAMESPACE=flow-alex
CHART_VERSION=8.9.0
VALUES_FILE=k8s/airflow-values.yml

# Install Airflow with Helm
echo "** Installing Airflow using Helm **"
helm install \
  $RELEASE_NAME \
  airflow-stable/airflow \
  --namespace $NAMESPACE \
  --version $CHART_VERSION \
  --values $VALUES_FILE

echo "** Airflow deployment completed successfully **"

echo "** Starting as postgres for apache airflow **"

helm repo add bitnami https://charts.bitnami.com/bitnami && helm repo update

helm install postgres bitnami/postgresql \
  --namespace flow-alex \
  --set global.postgresql.auth.username=airflow \
  --set global.postgresql.auth.password=airflow-password \
  --set global.postgresql.auth.database=airflow \
  --set primary.persistence.enabled=true \
  --set primary.persistence.size=10Gi

echo "**"
echo "** Done. **"

