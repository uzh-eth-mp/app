#!/bin/bash

set -e

source scripts/util/prepare-env.sh

# Add dev prefix
export PROJECT_NAME="$PROJECT_NAME-dev"
export DATA_DIR="$DATA_DIR-dev"

source scripts/util/compose-cleanup.sh
source scripts/util/prepare-data-dir.sh

# Start the containers in detached mode and
# attach the logs only to the data producers and consumers
docker compose \
    -p $PROJECT_NAME \
    -f docker-compose.yml \
    -f docker-compose.dev.yml \
    --profile eth up \
    --force-recreate \
    --build \
    --remove-orphans \
    -d && \
    docker compose -p $PROJECT_NAME logs \
    -f data_producer_eth data_consumer_eth
