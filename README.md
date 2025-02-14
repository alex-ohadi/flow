# Python Map Matcher in K8s Deployment  
**Author**: Alex O  
**Date**: Thurs, Feb 13 2025

---

### Project Overview

This project provides a Python-based map matcher that integrates with C++ functionality and runs in a Kubernetes environment.

---

### Key Files

- **Map Matcher Python Script**:  
  `flow/python/mapmatcher/map_matcher.py`

- **Map Matcher C++ File as Python Import**:  
  `flow/python/mapmatcher/mapmatcher.cpp`

- **Docker Compose**:  
  `flow/docker-compose.yml`

- **Python Dockerfile for Pulsar Connection**:  
  `flow/python/Dockerfile`

- **Kubernetes Deployment Files**:  
  `flow/k8s`,  
  `flow/start-as-k8s.sh`

---

### Prerequisites

Install the following dependencies:

```bash
brew install cmake              # for building the C++ file locally
brew install pybind11           # for building the C++ file locally
brew install nlohmann-json      # for building the C++ file locally
brew install colima             # for running Docker locally on mac
brew install docker             # for Docker
brew install docker-compose     # for containerization
brew install minikube           # for running K8s locally on mac
```

### Install Kubernetes Guide

For a detailed installation guide for Kubernetes on macOS, follow this link:  
[Install kubectl on macOS](https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/)

#### Instructions for Installing Kubernetes on Macs with Apple Chips:

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl"
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl.sha256"
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
sudo chown root: /usr/local/bin/kubectl
rm kubectl.sha256
brew install derailed/k9s/k9s
```

### Start Kubernetes: Run with K8s

1. **Start Minikube & Set Up Colima**:  
   Run `colima start --memory 4` for Pulsar.  
   Run `minikube start --driver=docker` (or for more resources: `minikube start --driver=docker --cpus=4 --memory=8192 --disk-size=20g`).

2. **Start K8s**:  
   - First, stop Docker containers:  
     `docker compose down -v`

   - Then, deploy with K8s:  
     `./start-as-k8s.sh`

3. **Monitor Pods** with `k9s`:  
   - Watch the map-matcher job run after it connects to Pulsar (~2 minutes).
   - View the logs and cron job with `kubectl get cronjob` or `kubectl get jobs`.

---

#### MongoDB in K8s: View Data for Matched GPS Segments

1. Run `k9s` and find the Mongo pod.
2. Press `s` on the Mongo pod to enter its shell, then use Mongo Shell:
   ```bash
   mongosh
   use data
   db.datas.find()
   ```

---

### Stop Kubernetes

To stop the Kubernetes deployment, use:  
`./stop-as-k8s.sh`

---

### *Optional* Start Docker: Run with docker

1. **Start As docker containers**  
   Run `colima start --memory 4` for Pulsar. 
   Run `docker volume create mongo_data_for_flow` to create mongo external volume
   Run `./start-docker-compose.sh`
2. **Login to Mongodb**
   ```bash
    docker exec -it <mongodb-container> sh
   mongosh
   use data
   db.datas.find()
   ```
3. **Stop Docker container**
   `docker compose down -v`
---


### *Optional* Start local build for testing (no mongo or pulsar)
- `cd flow/python/mapmatcher/`
- `rm -rf build;`
- `cmake -S . -B build -C CMakeLists-local.txt && make -C build` # uses local CMakeLists-local.txt
- `mv build/libhmm_map_matcher.so build/hmm_map_matcher.so`
- `python3 map-matcher.py`


### More Helpful MongoDB Commands

- **Start Mongo Shell**:  
  `mongosh`

- **List Databases**:  
  `show databases`

- **Use a Database**:  
  `use <database>`

- **Delete a Collection**:  
  ```bash
  use <database>
  show collections
  db.<collection>.drop()
  ```