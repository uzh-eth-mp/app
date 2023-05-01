#!/bin/bash

set -e
source scripts/util/prepare-env.sh

function cleanup {
    echo "Exiting production containters; starting cleanup..."
    docker compose -p $PROJECT_NAME down --remove-orphans
    echo "Cleanup successful."
}

read -p "Are you sure you want to stop the 'prod' containers (y/n)? " choice
case "$choice" in
  y|Y ) cleanup;;
  n|N ) echo "Ok - skipping...";;
  * ) echo "Invalid value.";;
esac
