#!/bin/bash

# Cleanup on exit or interrupt
function cleanup {
    echo "Starting cleanup; removing containers..."
    docker compose -p $PROJECT_NAME down --remove-orphans
    echo "Cleanup successful."
}
trap cleanup EXIT
