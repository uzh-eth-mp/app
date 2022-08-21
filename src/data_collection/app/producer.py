from datetime import datetime

from web3.exceptions import BlockNotFound

from app import init_logger
from app.data_collector import DataCollector
from app.kafka.manager import KafkaProducerManager
from app.node.block_explorer import BlockExplorer
from app.config import Config


log = init_logger(__name__)


class DataProducer(DataCollector):
    """
    Produce block / transaction data from the blockchain (node) to a Kafka topic.

    This class also updates the database with block data and saves the state
    of processing (latest_processed_block).
    """
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.config = config
        self.kafka_manager: KafkaProducerManager = KafkaProducerManager(
            kafka_url=config.kafka_url,
            topic=config.kafka_topic
        )

    async def start_data_fetching(self) -> None:
        """
        Start a while loop that collects all the block data
        based on the config values
        """
        # Get block exploration bounds (start and end block number)
        block_explorer = BlockExplorer(
            data_collection_cfg=self.config.data_collection,
            db=self.db_manager
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
        log.info(f"Starting from block #{start_block}, expecting to finish at {end_block_str}")
        try:
            while should_continue(i_block):
                # query the node for current block data
                block_data = await self.node_connector.get_block_data(i_block)

                # upsert the static block data to the block table
                await self.db_manager.insert_block(
                    block_number=block_data["number"],
                    block_hash=block_data["hash"].hex(),
                    nonce=block_data["nonce"].hex(),
                    difficulty=block_data["difficulty"],
                    gas_limit=block_data["gasLimit"],
                    gas_used=block_data["gasUsed"],
                    timestamp=datetime.fromtimestamp(block_data["timestamp"]),
                    miner=block_data["miner"],
                    parent_hash=block_data["parentHash"].hex(),
                    # TODO: need to calculate the block reward
                    # https://ethereum.stackexchange.com/questions/5958/how-to-query-the-amount-of-mining-reward-from-a-certain-block
                    block_reward=0,
                )

                # Send all the transaction hashes to Kafka so consumers can process them
                txs = list(map(lambda tx: tx.hex(), block_data["transactions"]))
                await self.kafka_manager.send_batch(msgs=txs)

                # upsert the latest processed block if the Kafka messages are
                # sent successfully
                i_processed_block = i_block
                await self.db_manager.upsert_last_processed_block_number(i_processed_block)

                # Continue from the next block
                i_block += 1

        except BlockNotFound:
            # OK, raised when the latest block is reached
            pass
        finally:
            if i_processed_block is None:
                log.info("Finished before collecting any block data.")
            else:
                log.info(f"Finished at block #{i_processed_block}")
