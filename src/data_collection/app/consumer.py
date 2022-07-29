from app import init_logger
from app.data_collector import DataCollector
from app.kafka.manager import KafkaConsumerManager
from app.config import Config


log = init_logger(__name__)


class DataConsumer(DataCollector):
    """
    Consume transaction hash from a given Kafka topic and save
    all required data to PostgreSQL.
    """

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.kafka_manager = KafkaConsumerManager(
            kafka_url=config.kafka_url,
            topic=config.kafka_topic
        )

    async def start_data_processing(self):
        """
        Start an infinite loop of consuming data from a given topic.
        """
        # Connect to Kafka
        await self.kafka_manager.start_consuming()

        # TODO: finish this method
