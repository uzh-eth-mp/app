from typing import List, Optional

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

    # Contains a list of smart contract addresses of interest.
    # Any transaction interacting (create, call) with these addresses
    # will be saved in the database.
    contracts: List[str]


class Config(BaseSettings):
    """Store an app configuration file"""

    # The blockchain node RPC API URL
    node_url: AnyUrl

    # PostgreSQL
    db_dsn: PostgresDsn

    # Redis URL
    redis_url: AnyUrl

    # Kafka
    kafka_url: str
    kafka_topic: str

    # Data collection related settings
    data_collection: DataCollectionConfig
