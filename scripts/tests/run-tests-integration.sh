#!/bin/bash

# Run integration tests
docker compose \
    -f docker-compose.tests.yml \
    up test_integration \
    --build \
    --abort-on-container-exit
