#!/bin/bash

set -e
source scripts/util/prepare-env.sh
source scripts/util/prepare-data-dir.sh $DATA_DIR $KAFKA_DATA_DIR $KAFKA_N_PARTITIONS
source scripts/util/compose-cleanup.sh

echo "Building containers..."

# Start the containers in detached mode
docker compose \
    -p $PROJECT_NAME \
    -f docker-compose.yml \
    -f docker-compose.prod.yml \
    --profile bsc up \
    --force-recreate \
    --build \
    --remove-orphans \
    -d

echo "Data collection starting..."

echo "Adding containers to network '${PROJECT_NAME}_default'"
docker network connect ${PROJECT_NAME}_default ${PROJECT_NAME}-data_producer_bsc-1

# Connect producer and each consumer (currently on the default 'bridge' network) to the compose network
docker ps --format '{{.Names}}' \
    | grep "consumer" \
    | while read c ; do {(docker network connect ${PROJECT_NAME}_default $c) &}; done
echo "Done; following container logs..."

# Show a warning message that keyboardinterrupt didn't execute a docker compose down
function warning {
    exit_status=$?
    echo "Note: the 'prod' containers are still running. View the logs with `./scripts/view-logs-prod-bsc.sh` or stop them with `./scripts/stop-prod-bsc.sh`."
    exit $exit_status
}
# Switch traps, from cleanup to a warning
trap - EXIT
trap warning EXIT

# attach the logs only to the data producers and consumers
docker compose \
    -p $PROJECT_NAME \
    logs \
    -f data_producer_bsc data_consumer_bsc
