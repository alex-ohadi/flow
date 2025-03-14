#!/bin/bash

echo "** Starting as k8s **"
# This deletes all <none> images automatically.
docker image prune -f

echo "** Build map matcher image **"
docker compose -f docker-compose.yml build --no-cache;

echo "** Let minikube know where the docker images are coming ** "
eval $(minikube docker-env)

cd k8s

echo "** Create Namesapce **"
kubectl apply -f ./namespaces

echo "** Set the flow-alex namespace for k9s for easy viewability later **"
kubectl config set-context --current --namespace=flow-alex || true


echo "** Create secrets to share between env variables**"
kubectl create secret generic env --from-env-file=../.env


echo "** Apply the configmaps, services, claims, deployments, and statefulset for the K8s manifests **"
kubectl apply -f ./config-maps
kubectl apply -f ./services
kubectl apply -f ./persistant-volume-claims
kubectl apply -f ./deployments

sleep 2

echo "****"
echo "** Success **"
echo "****"
echo "** Run k9s to view pods **"
echo "****"
echo "** Run ./stop-as-k8s.sh to stop"
echo "****"
echo "****"
echo "****"
echo "*** map-matcher job should run after it connects to pulsar (~2 minutes)."
echo "**** "

