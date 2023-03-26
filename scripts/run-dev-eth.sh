#!/bin/sh

# Directory where the data (PostgreSQL, Kafka) will be stored
export DATA_DIR=./data

# Linux workaround for docker container user/group permissions
mkdir -p \
    ./${DATA_DIR}/zookeeper-data/data \
    ./${DATA_DIR}/zookeeper-data/datalog \
    ./${DATA_DIR}/kafka-data \
    ./${DATA_DIR}/postgresql-data


export UID=$(id -u)
export GID=$(id -g)

# Start the containers in detached mode and
# attach the logs only to the data producers and consumers
docker compose \
    -f docker-compose.yml \
    -f docker-compose.dev.yml \
    --profile eth up \
    --force-recreate \
    --build \
    --remove-orphans \
    -d && \
    docker compose logs \
    -f data_producer_eth data_consumer_eth

docker compose down --remove-orphans
