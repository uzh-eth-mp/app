from typing import List

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock

from app.config import Config, DataCollectionConfig, ContractConfig
from app.model.abi import ContractABI
from app.model.transaction import (
    InternalTransactionData,
    TransactionData,
    TransactionReceiptData,
    TransactionLogsData,
)

shared_tx_hash = "0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822"


@pytest.fixture
def transaction_data() -> TransactionData:
    return TransactionData(
        **{
            "hash": shared_tx_hash,
            "blockNumber": 1337,
            "from": "0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
            "to": "0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
            "value": 42,
            "gasPrice": 135,
            "gas": 44423,
            "input": "0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
        }
    )


@pytest.fixture
def transaction_receipt_data() -> TransactionReceiptData:
    return TransactionReceiptData(
        **{
            "gasUsed": 1337,
            "logs": [],
            "type": "call",
            "contractAddress": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        }
    )


@pytest.fixture
def transaction_logs_data() -> TransactionLogsData:
    return TransactionLogsData(
        transactionHash=shared_tx_hash,
        address="0xf76de79a8cb78158f22dc8e0f3b6f3f6b9cd97d8",
        logIndex=1337,
        data="|Â¦E<",
        removed=False,
        topics=[
            "0x940c4b3549ef0aaff95807dc27f62d88ca15532d1bf535d7d63800f40395d16c",
            "0x000000000000000000000000e2de6d17b8314f7f182f698606a53a064b00ddcc",
            "0x0000000000000000000000005e42c86bb5352e9d985dd1200e05a35f4b0b2b14",
            "0x54494d4500000000000000000000000000000000000000000000000000000000",
        ],
    )


@pytest.fixture
def contract_abi() -> ContractABI:
    return ContractABI.parse_file("etc/contract_abi.json")


@pytest.fixture
def contract_config_usdt() -> ContractConfig:
    return ContractConfig(
        **{
            "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "symbol": "USDT",
            "category": "erc20",
            "events": [
                "TransferFungibleEvent",
                "MintFungibleEvent",
                "BurnFungibleEvent",
            ],
        }
    )


@pytest.fixture
def contract_config_compound() -> ContractConfig:
    return ContractConfig(
        **{
            "address": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
            "symbol": "Compound",
            "category": "erc20",
            "events": [
                "TransferFungibleEvent",
                "MintFungibleEvent",
                "BurnFungibleEvent",
            ],
        }
    )


@pytest.fixture
def contract_config_aave() -> ContractConfig:
    return ContractConfig(
        **{
            "address": "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9",
            "symbol": "Aave",
            "category": "erc20",
            "events": [
                "TransferFungibleEvent",
                "MintFungibleEvent",
                "BurnFungibleEvent",
            ],
        }
    )


@pytest.fixture
def contract_config_uniswapfactory() -> ContractConfig:
    return ContractConfig(
        **{
            "address": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
            "symbol": "UniSwap V2 Factory",
            "category": "UniSwapV2Factory",
            "events": [],
        }
    )


@pytest.fixture
def contract_config_pair_usdc_weth() -> ContractConfig:
    return ContractConfig(
        **{
            "address": "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc",
            "symbol": "UniSwap V2 Pair USDC-WETH",
            "category": "UniSwapV2Pair",
            "events": ["MintPairEvent", "BurnPairEvent", "SwapPairEvent"],
        }
    )


@pytest.fixture
def contract_config_pair_weth_usdt() -> ContractConfig:
    return ContractConfig(
        **{
            "address": "0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852",
            "symbol": "UniSwap V2 Pair WETH-USDT",
            "category": "UniSwapV2Pair",
            "events": ["MintPairEvent", "BurnPairEvent", "SwapPairEvent"],
        }
    )


@pytest.fixture
def data_collection_config_factory():
    def _data_collection_cfg(contracts: List[ContractConfig]):
        return DataCollectionConfig(
            **{
                "producer_type": "full",
                "start_block": 1337,
                "end_block": 1338,
                "contracts": contracts,
            }
        )

    return _data_collection_cfg


@pytest.fixture
def config_factory():
    def _config_factory(data_collection_cfg: List[DataCollectionConfig]):
        return Config(
            **{
                "node_url": "http://google.com",
                "db_dsn": "postgresql://muchuser:sopassword@wow:1337",
                "sentry_dsn": "nvm123",
                "redis_url": "redis://kek:1337",
                "kafka_url": "nvm123",
                "kafka_topic": "reeee",
                "data_collection": data_collection_cfg,
                "number_of_consumer_tasks": 1337,
                "web3_requests_timeout": 1337,
                "web3_requests_retry_limit": 1337,
                "web3_requests_retry_delay": 1337,
                "kafka_event_retrieval_timeout": 1337,
            }
        )

    return _config_factory


@pytest.fixture
def consumer_factory():
    def _consumer(config: Config, contract_abi: ContractABI):
        from app.consumer import DataConsumer

        consumer = DataConsumer(config, contract_abi)
        consumer.kafka_manager = MagicMock()
        consumer.db_manager = MagicMock()
        consumer.node_connector = MagicMock()
        consumer.contract_parser = MagicMock()
        return consumer

    return _consumer
