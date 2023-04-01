from typing import Any, List, Optional

from pydantic import (
    AnyUrl,
    BaseModel,
    BaseSettings,
    conlist,
    Field,
    root_validator,
    PostgresDsn,
)

from app.model.producer_type import ProducerType


class ContractConfig(BaseModel):
    """Describe a smart contract that the consumers should save data for

    For instance USDT, UniswapV2Factory or some UniswapPair
    """

    # The address of the smart contract
    address: str
    # The symbol / name / description of the contract
    symbol: str
    # The category of the contract. Mapped to contract.ContractCategory Enum.
    category: str

    def __eq__(self, __value: object) -> bool:
        return (
            self.address == __value.address
            and self.symbol == __value.symbol
            and self.category == __value.category
        )

    def __hash__(self) -> int:
        return hash(self.address + self.symbol + self.category)


class DataCollectionConfig(BaseSettings):
    """Store data collection configuration settings.

    Each data collection config will start producing transactions depending on its producer_type.
    """

    producer_type: ProducerType
    # The starting block number. Takes precedence over the setting in the db.
    start_block: Optional[int]
    # The ending block number. Takes precedence over the setting in the db.
    end_block: Optional[int]

    # Contains a list of smart contract objects of interest.
    # Any transaction interacting (create, call) with these addresses
    # will be saved in the database. Each contract contains information about
    # its category!
    contracts: List[ContractConfig]

    # Can be empty, required when used with ProducerType.LOG_FILTER
    topics: Optional[List[Any]]

    @root_validator
    def block_order_correct(cls, values):
        start_block = values.get("start_block")
        end_block = values.get("end_block")
        if start_block is not None and end_block is not None:
            # Verify that the end block is larger than start_block
            if start_block > end_block:
                raise ValueError(
                    f"start_block ({start_block}) must be equal or smaller than end_block ({end_block})"
                )

        return values

    @root_validator
    def producer_type_not_missing_topics(cls, values):
        """Validate topics not missing when producer_type = LOG_FILTER"""
        producer_type = values.get("producer_type")
        if producer_type == ProducerType.LOG_FILTER:
            if values.get("topics") is None:
                raise ValueError(
                    f'"producer_type": "log_filter" requires "topics" field'
                )
        return values


class Config(BaseSettings):
    """App configuration file"""

    node_url: AnyUrl
    """The blockchain node RPC API URL"""

    db_dsn: PostgresDsn
    """DSN for PostgreSQL"""

    redis_url: AnyUrl
    """URL for Redis (needs to have a 'redis://' scheme)"""

    kafka_url: str
    """URL for Kafka"""
    kafka_topic: str
    """The Kafka topic, also used in Redis and the database to distinguish tables."""

    data_collection: conlist(DataCollectionConfig, min_items=1)
    """(constrained) list of datacollection configurations"""

    number_of_consumer_tasks: int = Field(..., env="N_CONSUMER_INSTANCES")
    """The number of consumer (`DataConsumer`) tasks that will be started"""
