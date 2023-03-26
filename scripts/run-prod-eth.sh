#!/bin/sh

# Prefix for the containers and network
# "Blockchain Data Collection"
export PROJECT_NAME="bdc"
# Directory where the data (PostgreSQL, Kafka) will be stored
export DATA_DIR=/local/scratch/bdc/data

# Used for correct permissions (e.g. in PostgreSQL)
export UID=$(id -u)
export GID=$(getent group bdlt | cut -d: -f3)

# Linux workaround for docker container user/group permissions
mkdir -p \
    $DATA_DIR/zookeeper-data/data \
    $DATA_DIR/zookeeper-data/datalog \
    $DATA_DIR/kafka-data \
    $DATA_DIR/postgresql-data
chown -R $UID:$GID $DATA_DIR

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
