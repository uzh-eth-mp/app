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
    --profile all up \
    --force-recreate \
    --build \
    --remove-orphans \
    -d && \
    # connect the erigon proxy (on default bridge network) to the created compose network
    docker network connect ${PROJECT_NAME}_default ${PROJECT_NAME}-erigon_proxy && \
    # attach the logs only to the data producers and consumers
    docker compose -p $PROJECT_NAME logs \
    -f data_producer_eth data_producer_etc data_producer_bsc \
    data_consumer_eth data_consumer_etc data_consumer_bsc


docker compose down --remove-orphans