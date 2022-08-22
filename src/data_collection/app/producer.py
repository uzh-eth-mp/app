import asyncio

from app import init_logger
from app.data_collector import DataCollector
from app.kafka.manager import KafkaProducerManager
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
        self.kafka_manager = KafkaProducerManager(
            kafka_url=config.kafka_url,
            topic=config.kafka_topic
        )

    async def start_data_fetching(self) -> None:
        """
        Start a while loop that collects all the block data
        based on the config values
        """
        # Get the current latest block number
        latest_nr = await self.node_connector.get_latest_block_number()

        # Get the last block that was processed from the DB

        # if last == None: mine from latest to genesis
        # if latest > last: mine from latest to last
        # if last >= latest: do nothing

        while True:
            # query the node for current block data

            # upsert the static block data (blocknr, blockhash,
            # difficulty, ...) to the database

            # send all the transaction hashes to Kafka for
            # the data consumers to process them

            # upsert the latest processed block if the Kafka messages are
            # sent successfully


            # FIXME: remove next 2 lines
            await self.kafka_manager.send_message(f"Latest block nr: {latest_nr}")
            await asyncio.sleep(5)
