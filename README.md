## BACKEND
Author: Alex O
Thurs, Feb 13 2025

Python file that makes all this work:
 - flow/python/mapmatcher/shoopdawhoop.py

Map Matcher C++ file as python import:
 - flow/python/mapmatcher/mapmatcher.cpp

Docker Compose:
 - flow/docker-compose.yml

Dockerfile for Python Container that connects to Pulsar
 - flow/python/Dockerfile

**Install** 

- cmake, Docker, Docker Compose, Colima, pybind11
- `brew install cmake` # for building the cpp file locally
- `brew install pybind11` # for building the cpp file locally
- `brew install nlohmann-json` # for building the cpp file locally
- `brew install colima` # for running docker locally on mac
- `brew install docker`
- `brew install docker-compose`
- `brew install minikube` # for running k8s locally on mac
- Install Visual Studio
- Install Mongo Compass *Optional*

**Install Kubernetes**
https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/

**Instructions for Mac Apple Chips:**
-    `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl"`
- `   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl.sha256"`
- `chmod +x ./kubectl`
- `sudo mv ./kubectl /usr/local/bin/kubectl`
- `sudo chown root: /usr/local/bin/kubectl`
- `rm kubectl.sha256`
- `brew install derailed/k9s/k9s` 

# Note for local cmake: C library file location after build
flow/python/mapmatcher/build/build/libhmm_map_matcher.so
Note, it was created for architectures in the fat file: x86_64 & arm64 

## Local Test Run *Optional* (without pulsar or containerization)
How to build and run python script
- `cd flow/python/mapmatcher/`
- `rm -rf build;`
- `cmake -S . -B build -C CMakeLists-local.txt && make -C build` # uses local CMakeLists-local.txt
- `mv build/libhmm_map_matcher.so build/hmm_map_matcher.so`
- `python3 shoopdawhoop-local.py`


### Docker: Run as docker container
1. Create the external volume for database: 
  - `./create_mongo_data.sh`  (run once)
2. Start docker engine, memory settings are for pulsar: 
  - `colima start --memory 4` 
  - *If issues with colima try this* Add to ~/.bashrc : `echo 'export DOCKER_HOST="unix://$HOME/.colima/docker.sock"' >> ~/.bashrc && source ~/.bashrc`
3. Start docker containers:
  - `./start-docker-compose.sh`


## Kubernetes: Runs with K8s
1. Start minikube: 
 - `minikube start --driver=docker`
2. Start k8s:
 - `./start-as-k8s.sh`
3. Watch pods come up by running k9s, check pre-reqs to download it
 - `k9s`


**DOCKER COMMANDS**

Run `docker ps` to see the running containers

Run `docker map-matcher-alex-flow logs` 

Run `docker exec -it map-matcher-alex-flow sh  ` to go inside running container

**DOCKER COMMANDS**
Run `k9s` to see the running pods, press `[enter]` on the pods to view logs, or `s` to enter shell, or `d` to describe
Run `kubectl get events` to inspect errors


# Bring down stack
`docker compose down -v`


To use cmdline tables:
`mongosh`

list:
`show databases`
`use <database>`

delete:
`use <database>`
`show collections`
`db.<collection>.drop()`

show:
`use <database>`
`show collections`
`db.<collection>.find()`


Author: Alex Ohadi