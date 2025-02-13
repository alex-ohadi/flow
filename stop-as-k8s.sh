#!/bin/bash

echo "** Stopping k8s **"

cd k8s

echo "** Delete the configmaps, services, claims, deployments, and job for the K8s manifests **"
kubectl delete -f ./config-maps --ignore-not-found=true 
kubectl delete -f ./services --ignore-not-found=true
kubectl delete -f ./jobs --ignore-not-found=true
kubectl delete -f ./deployments --ignore-not-found=true
kubectl delete -f ./persistant-volume-claims --ignore-not-found=true

echo "** Delete Namesapce **"
kubectl delete -f ./namespaces  --ignore-not-found=true

echo "** Delete the secrets to share between env variables**"
kubectl delete secret env --ignore-not-found=true


# This deletes all <none> images automatically.
docker image prune -f
