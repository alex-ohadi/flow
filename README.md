# Python Map Matcher in K8s Deployment with Airflow 
**Author**: Alex O  
**Date**: Thurs, Feb 13 2025

---

### Project Overview

This project provides a Python-based map matcher that integrates with C++ functionality and runs in a Kubernetes environment. It also implements an Airflow job to restart the job at 12 UTC everyday.

---

### Key Files

- **Map Matcher Python Script**:  
  `flow/python/mapmatcher/map_matcher.py`

- **Map Matcher C++ File as Python Import**:  
  `flow/python/mapmatcher/mapmatcher.cpp`

- **Dockerfiles**:  
  `flow/python/Dockerfile`
  `flow/postgres/Dockerfile`

- **Kubernetes Deployment Files**:  
  `flow/k8s/deployments/`,  
  `flow/start-as-k8s.sh`
  `flow/stop-as-k8s.sh`

- **Airflow Values**
  `flow/k8s/airflow-values`
  `k8s_dag.py`

- **Docker Compose**:  
  `flow/docker-compose.yml`

---

### Prerequisites

Install the following dependencies:

```bash
brew install colima             # for running Docker locally on mac
brew install docker             # for Docker
brew install docker-compose     # for containerization
brew install minikube           # for running K8s locally on mac
brew install derailed/k9s/k9s
```

```bash
brew install cmake              # *optional* for local building the C++ file locally
brew install pybind11           # *optional* for local building the C++ file locally
brew install nlohmann-json      # *optional* for local building the C++ file locally
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
   **Note**: it is important to start colima/minikube with enough cpus and memory, in order to get Pulsar and Airflow working.
   Generally, the numbers set below should be enough for this setup, but adjust (raise/lower) depending on your Mac.
   - Run `colima start --cpu 4 --memory 8` for Pulsar.
   - Run `minikube start --driver=docker --cpus=2 --memory=7500`
   - Run `minikube -p minikube docker-env` for docker images
   - Run `eval $(minikube -p minikube docker-env)` so you can use *local docker images*, avoids error image pullback error


2. **Deploy Airflow** with helm
  - `kubectl apply -f ./k8s/namespaces`
  - `helm repo add apache-airflow https://airflow.apache.org && helm repo update`
  - `helm install airflow apache-airflow/airflow -n flow-alex -f k8s/airflow-values.yml`
  - *in a seperate terminal* `k9s`
  Wait until airflow pods are up by checking `k9s` (did you install k9s? `brew install derailed/k9s/k9s`)
  While in `k9s`, if the namespace does not directly show up, type `ns`, press enter, then navigate to the "flow-alex" namespace

3. **Start k8s manifests (deployments/configmaps/pvcs/etc)**:  
  - Deploy the rest of our manifests with k8s:  
     `./start-as-k8s.sh`
  - Monitor k9s, and wait for pulsar replicas to become ready

4. **Start map-matcher job**
  - This job will connect to pulsar and run the map-matcher python script, and will continue to re-connect if it's not ready yet:
   `kubectl create -f ./k8s/jobs/`

5. Once the map-matcher job shows completed (~2min), go back into your `k9s` terminal you opened in an earlier step,  to view the data in postgres after the map-matcher job runs (by checking logs of map-matcher) and find the postgres pod, then view the data by pressing `s` on the postgres pod to enter its shell, then from there you can interact with the database like so:
   ``` bash
    `psql -U flow -d data` # Select the database
    `SELECT COUNT(*) FROM datas;` # Show how many rows (show show 131 rows)
    `\pset pager off` # turn off pager
     `SELECT * FROM datas LIMIT 10; # Show the row data
   ```

7. **Airflow web interface**
  - Navigate to the web interface to view the airflow settings.
  - *In another seperate terminal*: `kubectl port-forward svc/airflow-webserver 8080:8080 -n flow-alex`
  - In a browser, navigate to `localhost:8080` and login with admin:admin

8. **Copy in the DAG to restart the map-matcher job everyday 12 UTC**
  - *In another seperate terminal*: `./k8s/update_dag.sh` # mount minikube
  - `kubectl cp ./k8s/k8s_dag.py flow-alex/airflow-worker-0:/opt/airflow/dags/`

9. **Airflow web interface**
  - In the the `k9s` terminal you opened in an earlier step, press [enter] on the airflow-worker-0 pod, and `s` into the worker.
    Inside worker:
    - Step 1) Go into the dags dir
      - `cd dags`
    - Step 2) Check errors with the DAG: 
      - `airflow dags list-import-errors` 
    - Step 3) Import the dag, this command will keep terminal open:
      -  `airflow scheduler`
    - Step 4) Refresh the dags folder in the web interface.
        - Debugging step: If still no new DAG, re-run webserver `kubectl port-forward svc/airflow-webserver 8080:8080 -n flow-alex`
    - Step 5) View and Trigger the Dag, by finding the map-matcher DAG, and pressing play
    - Step 6) Watch in `k9s`, as the map-matcher job gets recreated (runs delete/create on the job)


![k9s](instructions/terminals.png?raw=true "Open terminals handling setup")

![Airflow](instructions/airflow.png?raw=true "Airflow")

![GPS](instructions/GPStraces.png?raw=true "GPS")

![Pulsar](instructions/Pulsar.png?raw=true "Pulsar")

![Insert](instructions/Insert.png?raw=true "Insert")

![PG1](instructions/pg1.png?raw=true "PG1")

![PG2](instructions/pg2.png?raw=true "PG2")


### Common errors
1) If you build the images before running `eval $(minikube docker-env)` a docker image pullback issue might occur
2) Pulsar connection issues may happen due to increasing memory limits on colima and minikube
   - Run `colima start --cpu 4 --memory 8` for Pulsar.
   - Run `minikube start --driver=docker --cpus=2 --memory=7500`

### Stop Kubernetes

To stop the Kubernetes deployment, use:  
`./stop-as-k8s.sh`

---

# Optional Debugging Guide:

### *Optional* Start Docker: Run with docker

1. **Start As docker containers**  
   Run `colima start --cpu 4 --memory 4` for Pulsar. 
   Run `docker volume create postgres_data_for_flow` to create postgres external volume
   Run `./start-docker-compose.sh`
2. **Login to postgresdb**
   ```bash
    psql -U flow -d data
    SELECT COUNT(*) FROM datas;
    \pset pager off
    SELECT * FROM datas LIMIT 10;
   ```

3. **Stop Docker container**
   `docker compose down -v`
---


### *Optional* Start local build for testing (no postgres or pulsar)
- `cd flow/python/mapmatcher/`
- `rm -rf build;`
- `cmake -S . -B build -C CMakeLists-local.txt && make -C build` # uses local CMakeLists-local.txt
- `mv build/libhmm_map_matcher.so build/hmm_map_matcher.so`
- `python3 map-matcher.py`

### .env:
PGUSER=flow
POSTGRES_PASSWORD=flow-password
POSTGRES_DB=data
POSTGRES_USER=flow
POSTGRES_HOST=postgres-alex-flow
