#!/bin/bash

RETRIES=0
MAX_RETRIES=40

echo "Waiting for Kafka container to start...";

# Wait for PostgreSQL to start
while ! curl http://kafka:9092/ 2>&1 | grep '52' >/dev/null;
do
  sleep 1;

  # Respect maximum amount of retries
  (( RETRIES++ ))
  if [ $RETRIES -eq $MAX_RETRIES ]; then
    echo "Maximum retries ($RETRIES) reached."
    exit 1;
  fi
done

echo "Kafka container alive. Waiting 15s for Kafka startup script to finish..."
sleep 15;
