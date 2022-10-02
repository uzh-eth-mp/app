import asyncio

from web3.exceptions import BlockNotFound

from app import init_logger
from app.config import Config
from app.model.block import BlockData
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
    MAX_ALLOWED_TRANSACTIONS=50000

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.config = config
        self.kafka_manager: KafkaProducerManager = KafkaProducerManager(
            kafka_url=config.kafka_url,
            topic=config.kafka_topic
        )

    async def start_producing_data(self) -> None:
        """
        Start a while loop that collects all the block data from Web3
        based on the config values and inserts transactions into Kafka.
        """
        # Get block exploration bounds (start and end block number)
        block_explorer = BlockExplorer(
            data_collection_cfg=self.config.data_collection,
            db=self.db_manager,
            w3=self.node_connector
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
        pretty_config = self.config.dict(exclude={"node_url", "db_dsn", "redis_url", "kafka_url"})
        log.info(f'Using config: {pretty_config}')
        n_partitions = await self.kafka_manager.number_of_partitions
        log.info(f"Found {n_partitions} partition(s) on topic '{self.kafka_manager.topic}'")
        log.info(f"Starting from block #{start_block}, expecting to finish at {end_block_str}")

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
                log.debug(f"Block #{i_block}")

                # query the node for current block data
                block_data: BlockData = await self.node_connector.get_block_data(i_block)

                # Insert new block
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
                    log.info(f"Current block: {i_block}")
        except BlockNotFound:
            # OK, BlockNotFound exception is raised when the latest block is reached
            pass
        finally:
            if i_processed_block is None:
                log.info("Finished before collecting any block data.")
            else:
                log.info(f"Finished at block #{i_processed_block}")

    async def _insert_block(self, block_data: BlockData, block_reward: int):
        """Insert new block data into the block table"""
        block_data_dict = block_data.dict()
        # Remove unnecessary values
        del block_data_dict["transactions"]
        await self.db_manager.insert_block(
            **block_data_dict,
            # TODO: need to calculate the block reward
            # https://ethereum.stackexchange.com/questions/5958/how-to-query-the-amount-of-mining-reward-from-a-certain-block
            block_reward=block_reward
        )
