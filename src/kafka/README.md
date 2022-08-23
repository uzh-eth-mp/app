# Kafka

Modified entrypoint for Kafka to allow the previous zookeper session to expire. Otherwise, Kafka container will exit before zookeeper is able to drop the previous session and the whole app will fail.

Refer to [this link for more info](https://github.com/wurstmeister/kafka-docker/issues/389#issuecomment-800814529).
