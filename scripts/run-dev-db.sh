#!/bin/sh

docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build db

docker compose down --volumes --remove-orphans
