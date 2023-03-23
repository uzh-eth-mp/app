#!/bin/sh

# Linux workaround for docker container user/group
mkdir -p ./data/zookeeper-data/data ./data/zookeeper-data/datalog ./data/kafka-data ./data/postgresql-data

export UID=$(id -u)
export GID=$(id -g)

# Prefix for the containers and network
# "Blockchain Data Collection"
export PROJECT_NAME="bdc"

# Start the containers in detached mode
docker compose \
    -p $PROJECT_NAME \
    -f docker-compose.yml \
    -f docker-compose.prod.yml \
    --profile eth up \
    --force-recreate \
    --build \
    --remove-orphans \
    -d && \
    # connect the erigon proxy (on default bridge network) to the created compose network
    docker network connect ${PROJECT_NAME}_default ${PROJECT_NAME}-erigon_proxy && \
    # attach the logs only to the data producers and consumers
    docker compose -p $PROJECT_NAME logs \
    -f data_producer_eth
#    -f data_producer_eth data_consumer_eth

docker compose -p $PROJECT_NAME down --remove-orphans
