#!/bin/bash

# Get the current script directory and set the host directory path
SCRIPT_DIR=$(dirname "$(realpath "$0")")
export HOST_DIRECTORY="$SCRIPT_DIR/jobs"  # Export as environment variable

# Use the environment variable in the minikube mount command
minikube mount "$HOST_DIRECTORY:/mnt/data"