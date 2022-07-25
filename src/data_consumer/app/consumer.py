from app import init_logger
from app.config import Config
from app.kafka.manager import KafkaManager


log = init_logger(__name__)


class DataConsumer:
    """Manage Kafka, db and node operations"""

    def __init__(self, config: Config) -> None:
        self.kafka_manager = KafkaManager(
            kafka_url=config.kafka_url,
            topic=config.kafka_topic
        )

    async def start_data_processing(self):
        """
        Start an infinite loop of consuming data from a given topic.
        """
        # Connect to Kafka
        await self.kafka_manager.start()
        await self.kafka_manager.start_consuming()

        # TODO: finish this method