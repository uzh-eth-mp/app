from app import init_logger
from app.config import Config
from app.kafka.exceptions import KafkaManagerTimeoutError
from app.kafka.manager import KafkaConsumerManager
from app.model.abi import ERCABI
from app.model.transaction import TransactionData, TransactionReceiptData
from app.utils.data_collector import DataCollector
from app.web3.parser import ContractParser, ContractData
from app.web3.transaction_events import get_transaction_events
from app.web3.transaction_events.types import (
    MintFungibleEvent,
    BurnFungibleEvent,
    PairCreatedEvent,
    MintPairEvent,
    BurnPairEvent,
    SwapPairEvent,
    MintNonFungibleEvent,
    BurnNonFungibleEvent,
    TransferFungibleEvent,
    TransferNonFungibleEvent
)

log = init_logger(__name__)


class DataConsumer(DataCollector):
    """
    Consume transaction hash from a given Kafka topic and save
    all required data to PostgreSQL.
    """

    def __init__(self, config: Config, erc_abi: ERCABI) -> None:
        super().__init__(config)
        self.kafka_manager: KafkaConsumerManager = KafkaConsumerManager(
            kafka_url=config.kafka_url,
            topic=config.kafka_topic
        )
        # Extracts data from web3 smart contracts to a pydantic model
        self.contract_parser = ContractParser(
            web3=self.node_connector.w3,
            erc_abi=erc_abi
        )
        # A list of contract addresses that we should interact with
        self.known_contract_addresses = config.data_collection.contracts

        # Transaction hash of the currently processed transaction
        self._tx_hash = None

    def _should_handle_transaction(
        self, tx_data: TransactionData, tx_receipt_data: TransactionReceiptData
    ) -> bool:
        """Return True if the transaction interacts with a known contract address"""
        return \
            tx_data.to_address in self.known_contract_addresses or \
            tx_receipt_data.contract_address in self.known_contract_addresses

    async def _on_kafka_event(self, event):
        """Called when a new Kafka event is read from a topic"""
        # Get transaction hash from Kafka event
        self._tx_hash = event.value.decode()
        # Get transaction data
        tx_data: TransactionData = await self.node_connector.get_transaction_data(self._tx_hash)
        tx_receipt_data: TransactionReceiptData = \
            await self.node_connector.get_transaction_receipt_data(self._tx_hash)

        # Decrement the number of transactions in the queue
        await self.redis_manager.decr_n_transactions()

        log.debug(f"Received tx {tx_data.transaction_hash} in #{tx_data.block_number}")

        # Check if we should process this transaction or skip it
        if not self._should_handle_transaction(tx_data, tx_receipt_data):
            # Skip this transaction because it doesn't interact with
            # a known contract
            return
        log.debug(f"Handling tx {tx_data.transaction_hash} in #{tx_data.block_number}")

        # Check if transaction is creating a contract or calling it
        if not tx_data.to_address:
            # Transaction is creating a contract if to_address is None
            contract_address = tx_receipt_data.contract_address
            log.info(f"New contract ({contract_address}) creation in {tx_data.transaction_hash}")

            # 1. Get smart contract data (ERC20, ERC721 or ERC1151)
            contract_data: ContractData = await self.contract_parser.get_contract_data(
                contract_address=contract_address
            )

            if not contract_data:
                log.warning(f"Unknown contract ABI at address: {contract_address}")
                return

            # 2. Insert smart contract data into _contract and _token_contract table
            # in an SQL transaction
            async with self.db_manager.db.transaction():
                # _contract table
                await self.db_manager.insert_contract(
                    address=contract_data.address,
                    transaction_hash=tx_data.transaction_hash
                )
                # _token_contract table
                contract_data_dict = contract_data.dict()
                del contract_data_dict["code"]
                await self.db_manager.insert_token_contract(
                    **contract_data_dict
                )

        # Insert transaction + logs + internal
        # Get the rest of transaction data - compute transaction fee
        # (according to etherscan): fee = gas price * gas used
        gas_used = tx_receipt_data.gas_used
        tx_fee = tx_data.gas_price * gas_used

        # Insert the transaction and logs data
        async with self.db_manager.db.transaction():
            await self.db_manager.insert_transaction(
                **tx_data.dict(),
                gas_used=gas_used,
                is_token_tx=True,
                transaction_fee=tx_fee
            )
            for tx_log in tx_receipt_data.logs:
                await self.db_manager.insert_transaction_logs(**tx_log.dict())

        # TODO: check for AND insert internal transactions here if needed

        #Supply Change = mints - burns
        amount_changed = 0
        for event in get_transaction_events(contract_data.token_category, contract_data.w3_data, tx_receipt_data.w3_data):
            if isinstance(event, BurnFungibleEvent):
                amount_changed -= event.value
            elif isinstance(event, MintFungibleEvent):
                amount_changed += event.value
            #factory created a contract, store it in DB for future to check if it is pair contract.
            elif isinstance(event, TransferFungibleEvent):
                # TODO: store transfers?
                pass
            elif isinstance(event, PairCreatedEvent):
                # TODO: store contract pair was created.
                pass
            elif isinstance(event, MintPairEvent):
                # TODO: store a liquidity token was minted
                pass
            elif isinstance(event, BurnPairEvent):
                # TODO: store a liquidity token was burned
                pass
            elif isinstance(event, SwapPairEvent):
                # TODO: store a swap occurred in a liquidity pool
                pass
            elif isinstance(event, MintNonFungibleEvent):
                # TODO: store that an NFT was created.
                pass
            elif isinstance(event, BurnNonFungibleEvent):
                # TODO: store that an NFT was destroyed.
                pass
            elif isinstance(event, TransferNonFungibleEvent):
                # TODO: store that an NFT was destroyed.
                pass
        if amount_changed != 0:
            await self.db_manager.insert_contract_supply_change(
                address=contract_data.address,
                transaction_hash=tx_data.transaction_hash,
                amount_changed=amount_changed
            )

    async def start_consuming_data(self):
        """
        Start an infinite loop of consuming data from a given topic.
        """
        tx_hash = None
        try:
            # Start consuming events from a Kafka topic and
            # handle them in _on_kafka_event
            await self.kafka_manager.start_consuming(
                on_event_callback=self._on_kafka_event
            )
        except KafkaManagerTimeoutError:
            # Raised when a partition doesn't receive a new message for 60 seconds.
            log.info(f"Finished processing topic '{self.kafka_manager.topic}'. Shutting down...")
        except Exception as e:
            # Global handler for any exception, logs the transaction where this occurred
            # and reraises the exception.
            tx_hash = self._tx_hash or "first transaction"
            log.error(f"Caught exception during handling of {tx_hash}")
            raise e
