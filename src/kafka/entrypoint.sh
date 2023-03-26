#!/bin/bash

# Sleep is set to 10 seconds because the zookeeper.session.timeout.ms is 6s so we provide a little buffer
# for zookeeper to start.
# In short, we wait for the previously stored zookeeper session to expire, then we start
# Kafka and a new session is created. This prevents the Kafka container exiting with an error like it would
# while using the previous session.
echo "Sleeping for 10 seconds"
sleep 10

# Starting kafka as non-root
# inspired by https://github.com/wurstmeister/kafka-docker/issues/403#issuecomment-506345960
addgroup --gid $KAFKA_GID kafkausergroup
useradd -u $KAFKA_UID -g $KAFKA_GID $KAFKA_USER
chown -R $KAFKA_USER:$KAFKA_GID /kafka
chown -hLR $KAFKA_USER:$KAFKA_GID $KAFKA_HOME
chmod a+w -R $KAFKA_HOME
chown -R $KAFKA_USER /usr/bin/*.sh

echo "Running start-kafka.sh"
# Run as kafka user
exec su $KAFKA_USER -c '/bin/bash /usr/bin/start-kafka.sh'; wait
