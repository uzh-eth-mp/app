#!/bin/sh

# Linux workaround for docker container user/group
mkdir -p ./data/zookeeper-data/data ./data/zookeeper-data/datalog ./data/kafka-data ./data/postgresql-data

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
