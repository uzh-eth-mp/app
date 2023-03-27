import asyncio

from web3.exceptions import BlockNotFound

from app import init_logger
from app.config import Config, DataCollectionConfig
from app.model.block import BlockData
from app.model.producer_type import ProducerType
from app.kafka.manager import KafkaProducerManager
from app.web3.block_explorer import BlockExplorer
from app.utils.data_collector import DataCollector


log = init_logger(__name__)


class DataProducer(DataCollector):
    """
    Produce block / transaction data from the blockchain (node) to a Kafka topic.

    This class also updates the database with block data and saves the state
    of processing (latest_processed_block).
    """

    # The maximum amount of allowed transactions in a single kafka topic
    MAX_ALLOWED_TRANSACTIONS = 50000

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.config = config
        self.kafka_manager: KafkaProducerManager = KafkaProducerManager(
            kafka_url=config.kafka_url, topic=config.kafka_topic
        )

    async def _start_logfilter_producer(self, data_collection_cfg: DataCollectionConfig):
        """Start a log filter producer that sends only filtered transactions to kafka"""
        # TODO: Finish this method
        # as of now (March 2023) `eth_getFilterLogs` RPC method of the erigon node is unavailable
        # (https://github.com/ledgerwatch/erigon/issues/5092#issuecomment-1218133784)

        # Get list of addresses
        # addresses = list(map(lambda c: c.address, data_collection_cfg.contracts))
        # w3_filter = await self.node_connector.w3.eth.filter(
        #     {
        #         "address": addresses,
        #         "topics": data_collection_cfg.topics,
        #         "fromBlock": data_collection_cfg.start_block,
        #         "toBlock": data_collection_cfg.end_block
        #     }
        # )
        # result = await w3_filter.get_all_entries()
        # Continue in a similar fashion as in the full" producer method below
        # 1. Insert block if needed
        # 2. Send batch of txs to kafka
        # 3. Iterate until the end
        pass


    async def _start_full_producer(self, data_collection_cfg: DataCollectionConfig):
        """Start a regular (full) producer that goes through every block and sends all txs to kafka"""
        # Get block exploration bounds (start and end block number)
        block_explorer = BlockExplorer(
            data_collection_cfg=data_collection_cfg,
            db=self.db_manager,
            w3=self.node_connector,
        )
        start_block, end_block = await block_explorer.get_exploration_bounds()

        # Current block index, last processed block index
        i_block, i_processed_block = start_block, None

        if end_block is not None:
            # If end block contains a number, continue until we reach it
            should_continue = lambda i: i <= end_block
        else:
            # Else continue forever until a 'BlockNotFound' exception is raised
            should_continue = lambda _: True

        end_block_str = f"block #{end_block}" if end_block else "'latest' block"

        # Log information about the producer
        n_partitions = await self.kafka_manager.number_of_partitions
        log.info(
            f"Found {n_partitions} partition(s) on topic '{self.kafka_manager.topic}'"
        )
        log.info(
            f"Starting from block #{start_block}, expecting to finish at {end_block_str}"
        )

        # Start producing transactions
        try:
            while should_continue(i_block):
                # Verify that there is space in the Kafka topic for more transaction hashes
                if n_txs := await self.redis_manager.get_n_transactions():
                    if n_txs > self.MAX_ALLOWED_TRANSACTIONS:
                        # Sleep if there are many transactions in the kafka topic
                        await asyncio.sleep(1)
                        # Try again after sleeping
                        continue
                # query the node for current block data
                block_data: BlockData = await self.node_connector.get_block_data(
                    i_block
                )

                # Insert new block
                # FIXME: block reward
                await self._insert_block(block_data=block_data, block_reward=0)

                # Send all the transaction hashes to Kafka so consumers can process them
                await self.kafka_manager.send_batch(msgs=block_data.transactions)

                # Update the processed block variable with current block index
                i_processed_block = i_block

                # Increment the number of messages in a topic by the number of
                # transactions hashes in this block
                await self.redis_manager.incrby_n_transactions(
                    incr_by=len(block_data.transactions)
                )

                # Continue from the next block
                i_block += 1

                if (i_block - start_block) % 100 == 0:
                    log.info(f"Current block: #{i_block}")
        except BlockNotFound:
            # OK, BlockNotFound exception is raised when the latest block is reached
            pass
        finally:
            if i_processed_block is None:
                log.info("Finished before collecting any block data!")
            else:
                log.info(f"Finished at block #{i_processed_block}")


    async def _start_producer_task(self, data_collection_cfg: DataCollectionConfig) -> asyncio.Task:
        """
        Start a producer task depending on the data collection config producer type.
        """
        pretty_config = data_collection_cfg.dict(exclude={"contracts"})
        pretty_config["contracts"] = list(map(lambda c: c.symbol, data_collection_cfg.contracts))
        log.info(f"Creating data collection producer task ({pretty_config})")

        match data_collection_cfg.producer_type:
            case ProducerType.FULL:
                return asyncio.create_task(self._start_full_producer(data_collection_cfg))
            case ProducerType.LOG_FILTER:
                return asyncio.create_task(self._start_logfilter_producer(data_collection_cfg))

    async def start_producing_data(self) -> int:
        """
        Start a subproducer for each data collection config object and wait until they all finish.

        Returns:
            exit_code: 0 if no exceptions encountered during data collection, 1 otherwise
        """
        producer_tasks = []
        data_collection_configs = self.config.data_collection

        log.info(f"Using config: {self.config.dict(exclude={'data_collection'})}")

        # Create asyncio tasks for each data collection config
        for data_collection_cfg in data_collection_configs:
            producer_tasks.append(
                await self._start_producer_task(data_collection_cfg)
            )

        # Wait until all tasks finish
        result = await asyncio.gather(*producer_tasks, return_exceptions=True)
        exit_code = 0

        # Log exceptions if they occurred
        for (return_value, cfg) in zip(result, data_collection_configs):
            if isinstance(return_value, Exception):
                log.error(
                    f"Data collection for \"producer_type\"=\"{cfg.producer_type}\" with {len(cfg.contracts)} contracts resulted in an exception:",
                    exc_info=(type(return_value), return_value, return_value.__traceback__)
                )
                exit_code = 1

        log.info("Finished producing data from all data collection tasks.")
        return exit_code

    async def _insert_block(self, block_data: BlockData, block_reward: int):
        """Insert new block data into the block table"""
        block_data_dict = block_data.dict()
        # Remove unnecessary values
        del block_data_dict["transactions"]
        await self.db_manager.insert_block(
            **block_data_dict,
            # TODO: need to calculate the block reward
            # https://ethereum.stackexchange.com/questions/5958/how-to-query-the-amount-of-mining-reward-from-a-certain-block
            block_reward=block_reward,
        )
