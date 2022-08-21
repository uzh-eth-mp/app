from typing import Optional

from pydantic import (
    AnyUrl,
    BaseSettings,
    PostgresDsn
)


class DataCollectionConfig(BaseSettings):
    """Store data collection configuration settings."""
    # The starting block number. Takes precedence over the setting in the db.
    start_block: Optional[int]
    # The ending block number. Takes precedence over the setting in the db.
    end_block: Optional[int]


class Config(BaseSettings):
    """Store an app configuration file"""

    # The blockchain node RPC API URL
    node_url: AnyUrl

    # PostgreSQL
    db_dsn: PostgresDsn

    # Kafka
    kafka_url: str
    kafka_topic: str

    # Data collection related settings
    data_collection: DataCollectionConfig
