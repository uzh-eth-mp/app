from typing import List, Optional

from pydantic import AnyUrl, BaseModel, BaseSettings, root_validator, PostgresDsn


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


class DataCollectionConfig(BaseSettings):
    """Store data collection configuration settings."""

    # The starting block number. Takes precedence over the setting in the db.
    start_block: Optional[int]
    # The ending block number. Takes precedence over the setting in the db.
    end_block: Optional[int]

    # Contains a list of smart contract objects of interest.
    # Any transaction interacting (create, call) with these addresses
    # will be saved in the database. Each contract contains information about
    # its category!
    contracts: List[ContractConfig]

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
