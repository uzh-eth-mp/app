#!/bin/bash

set -e
source scripts/util/prepare-env.sh
source scripts/util/compose-cleanup.sh
source scripts/util/prepare-data-dir.sh

# Start the containers in detached mode
docker compose \
    -p $PROJECT_NAME \
    -f docker-compose.yml \
    -f docker-compose.prod.yml \
    --profile eth up \
    --force-recreate \
    --build \
    --remove-orphans \
    -d

echo "Adding containers to ${PROJECT_NAME}_default network"
docker network connect ${PROJECT_NAME}_default ${PROJECT_NAME}-data_producer_eth-1

# Connect producer and each consumer (currently on the default 'bridge' network) to the compose network
docker ps --format '{{.Names}}' \
    | grep "consumer" \
    | while read c ; do {(docker network connect ${PROJECT_NAME}_default $c) &}; done
echo "Done; following container logs..."

# attach the logs only to the data producers and consumers
docker compose \
    -p $PROJECT_NAME \
    logs \
    -f data_producer_eth data_consumer_eth
