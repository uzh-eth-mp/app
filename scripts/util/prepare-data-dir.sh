#!/bin/bash

# Linux workaround for docker container user/group permissions
mkdir -p \
    $DATA_DIR/zookeeper-data/data \
    $DATA_DIR/zookeeper-data/datalog \
    $DATA_DIR/kafka-data \
    $DATA_DIR/postgresql-data
chown -R $DATA_UID:$DATA_GID $DATA_DIR
