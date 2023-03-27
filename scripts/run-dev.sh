#!/bin/bash

set -e
source scripts/util/prepare-env.sh
source scripts/util/compose-cleanup.sh
source scripts/util/prepare-data-dir.sh

# Add dev prefix
PROJECT_NAME="dev-$PROJECT_NAME"

# Start the containers in detached mode and
# attach the logs only to the data producers
docker compose \
    -p $PROJECT_NAME \
    -f docker-compose.yml \
    -f docker-compose.dev.yml \
    --profile all up \
    --force-recreate \
    --build \
    --remove-orphans \
    -d && \
    docker compose -p $PROJECT_NAME logs \
    -f data_producer_eth data_producer_etc data_producer_bsc \
    data_consumer_eth data_consumer_etc data_consumer_bsc
