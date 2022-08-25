#!/bin/sh

# Run database tests
docker-compose \
    -f docker-compose.tests.yml \
    up test_db \
    --build \
    --abort-on-container-exit
