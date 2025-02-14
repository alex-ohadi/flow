#!/bin/bash

echo "** Stopping k8s **"

cd k8s

echo "** Deleting the jobs first to ensure no running workloads **"
kubectl delete -f ./jobs --ignore-not-found=true

echo "** Deleting statefulsets and deployments (workloads) **"
kubectl delete -f ./statefulset --ignore-not-found=true
kubectl delete -f ./deployments --ignore-not-found=true

echo "** Waiting for Deployments to be fully deleted **"
kubectl wait --for=delete deployment --all --timeout=60s

echo "** Deleting persistent volume claims (PVCs) after StatefulSet is gone **"
kubectl delete -f ./persistant-volume-claims --ignore-not-found=true

echo "** Deleting services, configmaps, and secrets **"
kubectl delete -f ./services --ignore-not-found=true
kubectl delete -f ./config-maps --ignore-not-found=true
kubectl delete secret env --ignore-not-found=true

echo "** Deleting Namespace **"
kubectl delete -f ./namespaces --ignore-not-found=true


# This deletes all <none> images automatically.
docker image prune -f
