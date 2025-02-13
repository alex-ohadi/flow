## BACKEND
Author: Alex Ohadi
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

- cmake, Docker, Docker Compose, Colima
- `brew install cmake`
- `brew install pybind11`
- `brew install colima`
- `brew install docker`
- `brew install docker-compose`
- Install Visual Studio
- Install Mongo Compass *Optional*

# Note for local cmake: C library file location after build
flow/python/mapmatcher/build/build/libhmm_map_matcher.so
Note, it was created for architectures in the fat file: x86_64 & arm64 

## Local Test Run *Optional* (without pulsar or containerization)
How to build and run python script
`cd flow/python/mapmatcher/`
`rm -rf build;`
`cmake -S . -B build && make -C build`
`mv build/libhmm_map_matcher.so build/hmm_map_matcher.so`
`python3 shoopdawhoop-local.py`




### START HERE: Run as docker container
1. Create the external volume for database: 
  - `./create_mongo_data.sh`  (run once)
2. Start docker engine, memory settings are for pulsar: 
  - `colima start --memory 4` 
  - *If issues with colima try this* Add to ~/.bashrc : `echo 'export DOCKER_HOST="unix://$HOME/.colima/docker.sock"' >> ~/.bashrc && source ~/.bashrc`
3. Start docker containers:
  - `./start.sh`


**DOCKER COMMANDS**

Run `docker ps` to see the running containers

Run `docker map-matcher-alex-flow logs` 

Run `docker exec -it map-matcher-alex-flow sh  ` to go inside running container

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