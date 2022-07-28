import asyncio

from aiokafka import AIOKafkaProducer
from aiokafka.errors import (
    KafkaError,
    KafkaTimeoutError,
    KafkaConnectionError
)

from app import init_logger


log = init_logger(__name__)


class KafkaManagerError(Exception):
    """Class for KafkaManager related errors"""
    pass


class KafkaManager:
    """
    Manage the Kafka cluster connection and allow producing
    messages to a selected topic.
    """
    # The delay before attempting the initial connection (in seconds)
    INITIAL_CONNECTION_DELAY = 30
    # The delay between connection attempts (in seconds)
    LINEAR_BACKOFF_DELAY = 5
    # The maximum allowed initial connection attempts before the app exits
    INITIAL_CONNECTION_MAX_ATTEMPTS = 15

    def __init__(self, kafka_url: str, topic: str) -> None:
        """
        Args:
            kafka_url: the url of the Kafka cluster
            topic: the Kafka topic
        """
        self.producer = AIOKafkaProducer(
            bootstrap_servers=kafka_url,
            enable_idempotence=True
        )
        self.topic = topic

    async def connect(self):
        """Connect (with linear backoff) to the kafka cluster.

        Note:
            Retrying with linear backoff is required as the
            startup time of Kafka is variable (usually 25-35s)
        """
        log.info(
            f"Waiting {self.INITIAL_CONNECTION_DELAY}s for Kafka to boot up"
        )
        await asyncio.sleep(self.INITIAL_CONNECTION_DELAY)

        log.info("Connecting to Kafka with linear backoff")
        connected, attempt_i = False, 0

        while not connected:
            # Check if we haven't reached max attempts
            attempt_i += 1
            if attempt_i > self.INITIAL_CONNECTION_MAX_ATTEMPTS:
                # Need to cleanup the producer before exiting.
                await self.producer.stop()
                # Exit the app if the max attempts have been reached
                raise KafkaManagerError(
                    "Maximum number of initial connection attempts reached."
                )
            # Try to connect to the cluster
            try:
                await self.producer.start()
                # If the call above doesn't raise an exception,
                # we're connected.
                connected = True
            except KafkaConnectionError as err:
                # Retry if we get an exception
                log.info(f"Connection failed - retrying in {self.LINEAR_BACKOFF_DELAY}s")
                await asyncio.sleep(self.LINEAR_BACKOFF_DELAY)
                continue
        log.info("Connected to Kafka")

    async def stop(self):
        """Flush pending data and disconnect from the kafka cluster"""
        log.info("Disconnecting from Kafka")
        await self.producer.stop()
        log.info("Disconnected from Kafka")

    async def send_message(self, msg: str):
        """Send message to a Kafka broker"""
        try:
            # Send the message
            send_future = await self.producer.send(
                topic=self.topic,
                value=msg.encode()
            )
            # Message will either be delivered or an unrecoverable
            # error will occur.
            _ = await send_future
        except KafkaTimeoutError:
            # Producer request timeout, message could have been sent to
            # the broker but there is no ack
            # TODO: somehow figure out whether this message should be
            # resent or not, maybe flag this message with a 'check_duplicate'
            # flag and let the consumer figure it out if these transactions are already
            # present in the database
            log.error(f"KafkaTimeoutError on {msg}")
        except KafkaError as err:
            # Generic kafka error
            log.error(f"{err} on {msg}")
            raise err
