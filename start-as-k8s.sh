#!/bin/bash

echo "** Starting as k8s **"

echo "** Deleting dangling images (host Docker) **"
docker images -f "dangling=true" -q | xargs -r docker rmi -f

echo "** Deleting flow* images (host Docker) **"
docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | grep '^pulsar' | awk '{print $2}' | xargs -r docker rmi -f

echo "** Switching to minikube Docker environment **"
eval $(minikube -p minikube docker-env)

echo "** Building images inside minikube **"
docker compose -f docker-compose.yml build --no-cache

cd k8s

echo "** Applying Kubernetes manifests **"
kubectl apply -f ./namespaces


echo "** Create Apache Pulsar In Dev Mode **"
helm repo add apache-pulsar https://pulsar.apache.org/charts
helm repo update

helm install my-pulsar apache-pulsar/pulsar -f pulsar-minikube.yml -f pod-monitors.yml

echo "** Setting namespace to flow-alex for kubectl and k9s **"
kubectl config set-context --current --namespace=flow-alex || true

echo "** Creating/updating secrets **"
kubectl delete secret env --ignore-not-found
kubectl create secret generic env --from-env-file=../.env

kubectl apply -f ./persistant-volume-claims
kubectl apply -f ./config-maps
kubectl apply -f ./services
kubectl apply -f ./deployments

echo "** Waiting for pods to be ready (optional) **"
# e.g. kubectl wait --for=condition=ready pod -l app=your-app -n flow-alex --timeout=120s

echo "****"
echo "** Success **"
echo "****"
echo "** Run k9s to view pods **"
echo "****"
echo "** Run ./stop-as-k8s.sh to stop **"
echo "****"
echo "*** map-matcher job should run after it connects to pulsar (~2 minutes)."
echo "**** "
