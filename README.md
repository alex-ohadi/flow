# Python Map Matcher in K8s Deployment with Airflow 
**Author**: Alex O  
**Date**: Thurs, Feb 13 2025

---

### Project Overview
This project is a map matching system that uses Python and C++ to process GPS data accurately. It runs in Kubernetes with Apache Pulsar handling messaging. A producer sends GPS events to Pulsar, and three consumer pods listen and run the map matching on the data. This setup allows fast, reliable, and scalable processing of GPS traces.


---

### Key Files

- **Map Matcher Python Script**:  
  `flow/producer/mapmatcher/map_matcher.py`

- **Map Matcher C++ File as Python Import**:  
  `flow/producer/mapmatcher/mapmatcher.cpp`

- **Dockerfiles**:  
  `flow/producer/Dockerfile`
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
       
       # *PREFERED* 
       # Mac M4 with 16GB of ram consideration: 
       - Run `colima start --cpu 4 --memory 12` for Pulsar.    
       - Run `minikube start --driver=docker --cpus=4 --memory=11000`


   - Run `minikube -p minikube docker-env` for docker images
   - Run `eval $(minikube -p minikube docker-env)` so you can use *local docker images*, avoids error image pullback error


2. **Apply Namespace** 
  - `kubectl apply -f ./k8s/namespaces`
  While in `k9s`, if the namespace does not directly show up, type `ns`, press enter, then navigate to the "flow-alex" namespace

3. **Start k8s manifests (deployments/configmaps/pvcs/etc)**:  
  - Deploy the rest of our manifests with k8s:  
     `./start-as-k8s.sh`
  - Monitor k9s, and wait for pulsar replicas to become ready

4. **Start map-matcher job & consumer**
  - This job will connect to pulsar and run the map-matcher python script, and will continue to re-connect if it's not ready yet:
   `kubectl apply -f ./k8s/jobs/`

5. Once the map-matcher job shows completed (~2min), go back into your `k9s` terminal you opened in an earlier step,  to view the data in postgres after the map-matcher job runs (by checking logs of map-matcher) and find the postgres pod, then view the data by pressing `s` on the postgres pod to enter its shell, then from there you can interact with the database like so:
   ``` bash
    `psql -U flow -d data` # Select the database
    `SELECT COUNT(*) FROM datas;` # Show how many rows (show show 131 rows)
    `\pset pager off` # turn off pager
     `SELECT * FROM datas LIMIT 10; # Show the row data
   ```

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

3) Kill namespace stuck in terminating:
`kubectl get namespace flow-alex -o json | jq 'del(.spec.finalizers)' | kubectl replace --raw "/api/v1/namespaces/flow-alex/finalize" -f -`

### Stop Kubernetes

To stop the Kubernetes deployment, use:  
`./stop-as-k8s.sh`

### .env:
PGUSER=flow
POSTGRES_PASSWORD=flow-password
POSTGRES_DB=data
POSTGRES_USER=flow
POSTGRES_HOST=pulsar-alex-postgres
