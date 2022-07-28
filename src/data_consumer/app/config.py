from pydantic import (
    BaseSettings,
    AnyUrl
)


class Config(BaseSettings):
    """Describes an app configuration file"""

    # The blockchain node RPC API URL
    node_url: AnyUrl

    # PostgreSQL
    db_dsn: AnyUrl

    # Kafka
    kafka_url: str
    kafka_topic: str
