from __future__ import annotations

from app.config import Config
from app.kafka.manager import KafkaManager
from app.web3.node_connector import NodeConnector
from app.db.manager import DatabaseManager
from app.db.redis import RedisManager


class DataCollector:
    """
    Superclass for DataConsumer and DataProducer

    Manages Kafka, PostgreSQL and node connections.
    """

    def __init__(self, config: Config) -> None:
        # Initialize the manager objects
        self.kafka_manager: KafkaManager = None
        self.node_connector = NodeConnector(node_url=config.node_url)
        self.db_manager = DatabaseManager(
            postgresql_dsn=config.db_dsn, node_name=config.kafka_topic
        )

    async def __aenter__(self) -> DataCollector:
        # Connect to Kafka
        await self.kafka_manager.connect()
        # Connect to the db
        await self.db_manager.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.kafka_manager.disconnect()
