#!/bin/bash

# Run web3 unit tests
docker compose \
    -f docker-compose.tests.yml \
    up test_web3 \
    --build \
    --abort-on-container-exit
