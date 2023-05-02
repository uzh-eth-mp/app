import logging

from web3.contract import Contract
from web3.types import TxReceipt, HexBytes

from app import init_logger
from app.config import Config
from app.kafka.exceptions import KafkaConsumerTopicEmptyError
from app.kafka.manager import KafkaConsumerManager
from app.model.abi import ContractABI
from app.model.contract import ContractCategory
from app.model.transaction import TransactionData, TransactionReceiptData
from app.utils.data_collector import DataCollector
from app.web3.parser import ContractParser
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
    TransferNonFungibleEvent,
)

log = init_logger(__name__)


class DataConsumer(DataCollector):
    """
    Consume transaction hash from a given Kafka topic and save
    all required data to PostgreSQL.
    """

    def __init__(self, config: Config, contract_abi: ContractABI) -> None:
        super().__init__(config)
        self.kafka_manager: KafkaConsumerManager = KafkaConsumerManager(
            kafka_url=config.kafka_url,
            redis_url=config.redis_url,
            topic=config.kafka_topic,
        )
        # Create a set from all the contracts (we want to save any of these transactions)
        contracts = set()
        for data_cfg in config.data_collection:
            contracts = contracts.union(set(data_cfg.contracts))

        # Extracts data from web3 smart contracts
        self.contract_parser = ContractParser(
            web3=self.node_connector.w3,
            contract_abi=contract_abi,
            contracts=contracts,
        )

        # Transaction hash of the currently processed transaction
        self._tx_hash = None

        # Keep a number of consumed (from Kafka) and processed transactions
        self._n_consumed_txs = 0
        self._n_processed_txs = 0

        # Filter out some kafka logs
        def kafka_logs_filter(record) -> bool:
            msg = record.getMessage()
            should_filter = msg.startswith(
                "Heartbeat failed for group"
            ) or msg.startswith("Group Coordinator Request failed:")
            return not should_filter

        kafka_logger = logging.getLogger("aiokafka.consumer.group_coordinator")
        kafka_logger.addFilter(kafka_logs_filter)

    async def _handle_contract_creation(
        self, contract: Contract, tx_data: TransactionData, category: ContractCategory
    ):
        """Insert required contract data into the database depending on its category"""
        # Transaction is creating a contract if to_address is None
        log.info(
            f"New contract ({contract.address}) creation in {tx_data.transaction_hash}"
        )

        if category.is_erc:
            # If the contract is an ERC contract,
            # get token contract data (ERC20, ERC721 or ERC1151)
            token_contract_data = await self.contract_parser.get_token_contract_data(
                contract=contract, category=category
            )

            if not token_contract_data:
                log.warning(
                    f"Unknown token contract ABI at address: {contract.address}"
                )
                return

            # Insert token contract data into _contract and _token_contract table
            # in an SQL transaction
            async with self.db_manager.db.transaction():
                # _contract table
                await self.db_manager.insert_contract(
                    address=token_contract_data.address,
                    transaction_hash=tx_data.transaction_hash,
                )
                # _token_contract table
                await self.db_manager.insert_token_contract(
                    **token_contract_data.dict()
                )
        elif category.is_uniswap_pair:
            # If the contract is a pair contract
            pair_contract_data = await self.contract_parser.get_pair_contract_data(
                contract=contract, category=category
            )

            if not pair_contract_data:
                log.warning(f"Unknown pair contract ABI at address: {contract.address}")
                return

            # Insert pair contract data into _contract and _pair_contract table
            # in an SQL transaction
            async with self.db_manager.db.transaction():
                # _contract table
                await self.db_manager.insert_contract(
                    address=pair_contract_data.address,
                    transaction_hash=tx_data.transaction_hash,
                )
                # _token_contract table
                # TODO: await self.db_manager.insert_pair_contract()
                await self.db_manager.insert_pair_contract(**pair_contract_data.dict())

        return contract

    async def _handle_transaction(
        self, tx_data: TransactionData, tx_receipt_data: TransactionReceiptData
    ):
        """Insert transaction data into the database"""
        # Get the rest of transaction data - compute transaction fee
        # (according to etherscan): fee = gas price * gas used
        gas_used = tx_receipt_data.gas_used
        tx_fee = tx_data.gas_price * gas_used

        # Insert the transaction and logs data
        await self.db_manager.insert_transaction(
            **tx_data.dict(),
            gas_used=gas_used,
            is_token_tx=True,
            transaction_fee=tx_fee,
        )

        # check for AND insert internal transactions if needed
        internal_tx_data = await self.node_connector.get_internal_transactions(
            self._tx_hash
        )
        if internal_tx_data:
            async with self.db_manager.db.transaction():
                for internal_tx in internal_tx_data:
                    await self.db_manager.insert_internal_transaction(
                        **internal_tx.dict(), transaction_hash=tx_data.transaction_hash
                    )

    async def _handle_transaction_events(
        self,
        contract: Contract,
        category: ContractCategory,
        tx_data: TransactionData,
        tx_receipt: TxReceipt,
        tx_receipt_data: TransactionReceiptData,
        w3_block_hash: HexBytes,
    ):
        """Insert transaction events (supply changes) into the database"""
        allowed_events = self.contract_parser.get_contract_events(contract.address)
        # Keep a list of 'logIndex' for logs that should be saved
        log_indices_to_save = set()
        # log.debug(f"Extracting transaction events from contract {contract.address}")
        # Supply Change = mints - burns
        amount_changed = 0
        pair_amount0_changed = 0
        pair_amount1_changed = 0
        for event, event_log in get_transaction_events(
            category, contract, tx_receipt, w3_block_hash
        ):
            # Check if this event should be processed
            if not type(event).__name__ in allowed_events:
                continue
            # Mark this log to be saved
            log_indices_to_save.add(event_log["logIndex"])

            # log.debug(f"Caught event ({event.__class__.__name__}): {event}")
            if isinstance(event, BurnFungibleEvent):
                amount_changed -= event.value
            elif isinstance(event, MintFungibleEvent):
                amount_changed += event.value
            elif isinstance(event, TransferFungibleEvent):
                pass
            elif isinstance(event, PairCreatedEvent):
                pass
            elif isinstance(event, MintPairEvent):
                pair_amount0_changed += event.amount0
                pair_amount1_changed += event.amount1
            elif isinstance(event, BurnPairEvent):
                pair_amount0_changed -= event.amount0
                pair_amount1_changed -= event.amount1
            elif isinstance(event, SwapPairEvent):
                # Swap is like a mint + burn, with different ratios
                pair_amount0_changed += event.in0
                pair_amount1_changed += event.in1
                pair_amount0_changed -= event.out0
                pair_amount1_changed -= event.out1
            elif isinstance(event, MintNonFungibleEvent):
                pass
            elif isinstance(event, BurnNonFungibleEvent):
                pass
            elif isinstance(event, TransferNonFungibleEvent):
                pass

        # Insert the transaction logs into DB
        logs_to_save = [
            log for log in tx_receipt_data.logs if log.log_index in log_indices_to_save
        ]
        async with self.db_manager.db.transaction():
            for tx_log in logs_to_save:
                await self.db_manager.insert_transaction_logs(**tx_log.dict())

        # Insert specific events into DB
        if amount_changed != 0:
            await self.db_manager.insert_contract_supply_change(
                address=contract.address,
                transaction_hash=tx_data.transaction_hash,
                amount_changed=amount_changed,
            )
        # log.debug(f"pair_amount0_changed= {pair_amount0_changed} pair_amount1_changed= {pair_amount1_changed}")
        if pair_amount0_changed != 0 or pair_amount1_changed != 0:
            await self.db_manager.insert_pair_liquidity_change(
                address=contract.address,
                amount0=pair_amount0_changed,
                amount1=pair_amount1_changed,
                transaction_hash=tx_data.transaction_hash,
            )

    async def _on_kafka_event(self, event):
        """Called when a new Kafka event is read from a topic"""
        # Get transaction hash from Kafka event
        self._tx_hash = event.value.decode()
        # Increment number of consumed transactions
        self._n_consumed_txs += 1
        # Get transaction data
        tx_data, w3_tx_data = await self.node_connector.get_transaction_data(
            self._tx_hash
        )
        (
            tx_receipt_data,
            w3_tx_receipt,
        ) = await self.node_connector.get_transaction_receipt_data(self._tx_hash)
        # Select the address that this transaction interacts with or creates
        contract_address = tx_data.to_address or tx_receipt_data.contract_address
        contract_category = self.contract_parser.get_contract_category(contract_address)

        # log.debug(f"Received tx {tx_data.transaction_hash} in #{tx_data.block_number}")

        # Check if we should process this transaction or skip it
        if contract_category is None:
            # Skip this transaction because it doesn't interact with
            # a known contract
            return
        # log.debug(f"Handling tx {tx_data.transaction_hash} in #{tx_data.block_number}")
        # Increment number of processed transactions
        self._n_processed_txs += 1
        # Check if transaction is creating a contract or calling it
        contract = self.contract_parser.get_contract(
            contract_address=contract_address, category=contract_category
        )
        # 1. Contract creation
        if not tx_data.to_address:
            await self._handle_contract_creation(
                contract=contract, tx_data=tx_data, category=contract_category
            )

        # 2. Insert transaction + Internal transactions
        await self._handle_transaction(tx_data=tx_data, tx_receipt_data=tx_receipt_data)

        # 3. Transaction events
        await self._handle_transaction_events(
            contract=contract,
            category=contract_category,
            tx_data=tx_data,
            tx_receipt=w3_tx_receipt,
            tx_receipt_data=tx_receipt_data,
            w3_block_hash=w3_tx_data["blockHash"],
        )

    async def start_consuming_data(self) -> int:
        """
        Start an infinite loop of consuming data from a given topic.

        Returns:
            exit_code: 0 if no exceptions encountered during data collection, 1 otherwise
        """
        exit_code = 0
        try:
            # Start consuming events from a Kafka topic and
            # handle them in _on_kafka_event
            await self.kafka_manager.start_consuming(
                on_event_callback=self._on_kafka_event
            )
        except KafkaConsumerTopicEmptyError:
            # Raised when a partition doesn't receive a new message for 120 seconds.
            log.info(f"Finished processing topic '{self.kafka_manager.topic}'.")
            # exit_code doesn't change, 0 = success
        except Exception as e:
            # Global handler for any exception, logs the transaction where this occurred
            # and returns exit code 1
            tx_hash = self._tx_hash or "first transaction"
            log.error(
                f"Caught exception during handling of {tx_hash}",
                exc_info=(type(e), e, e.__traceback__),
            )
            exit_code = 1
        finally:
            log.info(
                "number of consumed transactions: {} | number of processed transactions: {}".format(
                    self._n_consumed_txs, self._n_processed_txs
                )
            )
            return exit_code
