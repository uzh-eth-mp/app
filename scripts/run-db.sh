#!/bin/bash

set -e

# Cleanup
trap "docker compose down --volumes --remove-orphans" EXIT

# Env vars
source scripts/prepare-env.sh

# Start the db
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build db
