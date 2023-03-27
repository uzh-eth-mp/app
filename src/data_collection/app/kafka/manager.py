import asyncio

from asyncio import TimeoutError
from typing import Awaitable, Callable, List

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError, KafkaTimeoutError, KafkaConnectionError

from app import init_logger
from app.kafka.exceptions import (
    KafkaManagerError,
    KafkaConsumerTopicEmptyError,
    KafkaConsumerTimeoutError,
)


log = init_logger(__name__)


class KafkaManager:
    """
    Manage the Kafka cluster connection.
    Base class for KafkaProducerManager and KafkaConsumerManager.
    """

    # The delay between connection attempts (in seconds)
    LINEAR_BACKOFF_DELAY = 5
    # The maximum allowed initial connection attempts before the app exits
    INITIAL_CONNECTION_MAX_ATTEMPTS = 10

    def __init__(self, kafka_url: str, topic: str) -> None:
        """
        Args:
            kafka_url: the url of the Kafka cluster
            topic: the Kafka topic
        """
        self.topic = topic
        self._client = None

    async def connect(self):
        """Connect (with linear backoff) to the kafka cluster.

        Note:
            Retrying with linear backoff is required as the
            startup time of Kafka is variable (usually 25-35s)
        """
        connected, attempt_i = False, 0

        while not connected:
            # Check if we haven't reached max attempts
            attempt_i += 1
            if attempt_i > self.INITIAL_CONNECTION_MAX_ATTEMPTS:
                # Need to cleanup the producer before exiting.
                await self._client.stop()
                # Exit the app if the max attempts have been reached
                raise KafkaManagerError(
                    "Maximum number of initial connection attempts reached."
                )
            # Try to connect to the cluster
            try:
                await self._client.start()
                # If the call above doesn't raise an exception,
                # we're connected.
                connected = True
            except KafkaConnectionError as err:
                # Retry if we get an exception
                log.info(
                    f"Connection failed - retrying in {self.LINEAR_BACKOFF_DELAY}s"
                )
                await asyncio.sleep(self.LINEAR_BACKOFF_DELAY)
                continue
        log.debug("Connected to Kafka")

    async def disconnect(self):
        """Flush pending data and disconnect from the kafka cluster"""
        await self._client.stop()
        log.debug("Disconnected from Kafka")


class KafkaProducerManager(KafkaManager):
    """Manage producing events to a given Kafka topic"""

    def __init__(self, kafka_url: str, topic: str) -> None:
        super().__init__(kafka_url, topic)
        self._client = AIOKafkaProducer(
            bootstrap_servers=kafka_url, enable_idempotence=True
        )
        # The currently selected partition that will receive the next batch
        self.i_partition = 0

    @property
    async def number_of_partitions(self) -> int:
        """Return the number of partitions in this topic"""
        partitions = await self._client.partitions_for(self.topic)
        return len(partitions)

    async def send_message(self, msg: str):
        """Send message to a Kafka broker"""
        try:
            # Send the message
            send_future = await self._client.send(topic=self.topic, value=msg.encode())
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

    async def send_batch(self, msgs: List[str]):
        """Send a batch of messages to a Kafka broker"""
        try:
            kafka_batch = self._client.create_batch()

            for msg in msgs:
                # key and timestamp arguments are required
                kafka_batch.append(key=None, value=msg.encode(), timestamp=None)

            kafka_batch.close()

            # Add the batch to the first partition's submission queue. If this method
            # times out, we can say for sure that batch will never be sent.
            send_fut = await self._client.send_batch(
                kafka_batch, self.topic, partition=self.i_partition
            )

            # Batch will either be delivered or an unrecoverable error will occur.
            # Cancelling this future will not cancel the send.
            _ = await send_fut

            # Increment the partition counter so that the next batch will be sent onto another partition
            self.i_partition += 1
            if self.i_partition == await self.number_of_partitions:
                # Roll over to partition 0 if we reach the last partition
                self.i_partition = 0
        except KafkaTimeoutError:
            # Producer request timeout, message could have been sent to
            # the broker but there is no ack
            # TODO: somehow figure out whether this message should be
            # resent or not, maybe flag this message with a 'check_duplicate'
            # flag and let the consumer figure it out if these transactions are already
            # present in the database
            log.error(f"KafkaTimeoutError on batch")


class KafkaConsumerManager(KafkaManager):
    """Manage consuming events from a given Kafka topic"""

    # How much time (in seconds) to wait for the next event / message
    # from a Kafka topic before exiting
    EVENT_RETRIEVAL_TIMEOUT = 120

    def __init__(self, kafka_url: str, topic: str) -> None:
        super().__init__(kafka_url, topic)
        self._client = AIOKafkaConsumer(
            topic,
            bootstrap_servers=kafka_url,
            group_id=topic,
            auto_offset_reset="earliest",
        )
        # True if an event was received. False otherwise.
        self._event_received = False

    async def _event_timeout(self, event):
        """Raise an exception if event.set() is not called for EVENT_RETRIEVAL_TIMEOUT seconds"""
        while True:
            # Wait for event.set() to be called for EVENT_RETRIEVAL_TIMEOUT seconds
            await asyncio.wait_for(event.wait(), self.EVENT_RETRIEVAL_TIMEOUT)
            # Reset the event timeout to wait another 30 seconds for a new Kafka event
            event.clear()

    async def _start_listening_on_topic(
        self,
        on_event_callback: Callable[[str], Awaitable[None]],
        wait_event: asyncio.Event,
    ):
        """Listen for new Kafka messages on a predefined topic"""
        try:
            # Wait for new events from Kafka and call the callback
            async for event in self._client:
                # Notify the wait_event that we've received a new Kafka topic event
                wait_event.set()
                # Await the async callback
                await on_event_callback(event)
        except TimeoutError as e:
            raise KafkaConsumerTopicEmptyError from e

    async def start_consuming(
        self, on_event_callback: Callable[[str], Awaitable[None]]
    ):
        """Consume messages from a given topic and generate (yield) events"""
        try:
            partitions = list(map(lambda p: p.partition, self._client.assignment()))
            log.info(
                f"Consuming events in topic '{self.topic}' for partitions: {partitions}"
            )

            # Create an asyncio Event that is used for timing out
            # when no message from Kafka is received for some time
            wait_event = asyncio.Event()

            # Create a consume task
            consume_task = asyncio.create_task(
                self._start_listening_on_topic(on_event_callback, wait_event)
            )

            # Create a task for a timeout to run in the background
            timeout_task = asyncio.create_task(self._event_timeout(wait_event))

            # Wait for consuming to finish
            # (with a timeout task that can interrupt the consume task by raising an exception)
            await asyncio.gather(timeout_task, consume_task)

        except TimeoutError:
            # Raised when no message is received within the specified time
            log.info(
                f"No event received for {self.EVENT_RETRIEVAL_TIMEOUT} seconds - timed out"
            )
            raise KafkaConsumerTopicEmptyError
        finally:
            # Disconnect from Kafka
            await self.disconnect()
