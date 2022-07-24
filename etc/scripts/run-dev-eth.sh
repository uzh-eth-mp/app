#!/bin/sh

# Start the containers in detached mode and
# attach the logs only to the data producers
docker-compose \
    -f docker-compose.yml \
    -f docker-compose.dev.yml \
    --profile eth up \
    --force-recreate \
    --build \
    --remove-orphans \
    -d && \
    docker-compose logs \
    -f data_producer_eth

docker-compose down --remove-orphans