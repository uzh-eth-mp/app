#!/bin/bash

RETRIES=0

# Wait for PostgreSQL to start
while ! curl http://$POSTGRES_HOST:$POSTGRES_PORT/ 2>&1 | grep '52';
do
  sleep 1;
  echo "Waiting 1s for PostgreSQL container to start.";

  # Respect maximum amount of retries
  (( RETRIES++ ))
  if [ $RETRIES -eq 15 ]; then
    echo "Maximum retries ($RETRIES) reached."
    exit 1;
  fi
done
