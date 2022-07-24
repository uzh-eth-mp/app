from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError, KafkaTimeoutError

from app import init_logger


log = init_logger(__name__)


class KafkaManager:
    """Manage the Kafka connection and produce messages"""

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

    async def start(self):
        """Connect to the kafka cluster"""
        log.info("Connecting to Kafka")
        await self.producer.start()
        log.info("Connected to Kafka")


    async def stop(self):
        """Flush pending data and disconnect from the kafka cluster"""
        log.info("Disconnecting from Kafka")
        await self.producer.stop()
        log.info("Disconnected from Kafka")

    async def send_message(self, msg):
        try:
            send_future = await self.producer.send(
                topic=self.topic,
                value=msg
            )
            # Message will either be delivered or an unrecoverable
            # error will occur.
            response = await send_future
        except KafkaTimeoutError:
            # Producer request timeout, message could have been sent to
            # the broker but there is no ack
            # TODO: somehow figure out whether this message should be
            # resent or not, maybe flag this message with a 'check_duplicate'
            # flag and let the consumer figure it out if these transactions are already
            # present in the database
            log.error(f"KafkaTimeoutError on {msg}")
        except KafkaError as err:
            log.err(f"{err} on {msg}")
            raise err
