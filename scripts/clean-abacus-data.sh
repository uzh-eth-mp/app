#!/bin/sh

DATA_DIR=./data

docker run --rm -v ${DATA_DIR}:/tmprm ubuntu rm -r /tmprm/kafka-data
docker run --rm -v ${DATA_DIR}:/tmprm ubuntu rm -r /tmprm/zookeeper-data
rm -r ${DATA_DIR}
