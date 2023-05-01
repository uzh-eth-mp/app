#!/bin/bash

set -e
source scripts/util/prepare-env.sh

docker compose -p $PROJECT_NAME down --remove-orphans
