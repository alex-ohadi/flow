## BACKEND

**Install** 

- cmake, Docker, Docker Compose, Colima
- `brew install cmake`
- `brew install pybind11`
- `brew install colima`
- `colima start --memory 4` for pulsar
- `brew install docker`
- `brew install docker-compose`

- Install Visual Studio
- Install Mongo Compass

# C library file location
flow/python/mapmatcher/build/build/libhmm_map_matcher.so
Architectures in the fat file: libhmm_map_matcher.so are: x86_64 arm64 


##
How to build and run python script
`cd flow/python/mapmatcher/`
`rm -rf build;`
`cmake -S . -B build`
`cd build`
`make`
`cd ..`
`mv build/libhmm_map_matcher.so build/hmm_map_matcher.so`
`python3 shoopdawhoop.py`


***Prerequisites***
To get started run:
`sudo npm install`

Add .env and .env-prod to your directory from Github Owner

### Run as docker container

# LOCAL
1. Create the external volume for database: 
  - `./create_mongo_data.sh`  (run once)
2. Start docker engine: 
  - `colima start` (run once) 
3. - Add to ~/.bashrc : `echo 'export DOCKER_HOST="unix://$HOME/.colima/docker.sock"' >> ~/.bashrc && source ~/.bashrc`
5. Start docker containers:
  - `./start.sh`


# PROD
1. Create the external volume for database: 
 - `./create_mongo_data.sh` (run once)
2. Start docker containers:
 -  `./start-prod.sh`

**DOCKER COMMANDS**

Run `docker ps` to see the running containers

Run `docker python logs` 

Run `docker exec -it python sh` to go inside running container


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


# Logs:

`cd /var/log/mongodb/`
`tail -f mongod.log | jq`

or 

`docker logs --follow <mongo_id> | jq`


# For apple M1 chips;

colima start --arch aarch64 --no-qemu

# Mongo Examples:

Login:
mongosh --port 27017 -u "<user_name>" --authenticationDatabase "<db_name>" -p "<password>"

Show Collection:
use <db_name>
show collections
db.<collection>.find()

