from app import init_logger
from app.config import Config
from app.kafka.manager import KafkaManager
from app.node.connector import NodeConnector


log = init_logger(__name__)


class DataProducer:
    """Manage Kafka, db and node operations"""

    def __init__(self, config: Config) -> None:
        self.kafka_manager = KafkaManager(
            kafka_url=config.kafka_url,
            topic=config.kafka_topic
        )
        self.node_connector = NodeConnector(
            node_url=config.node_url
        )

    async def start_data_fetching(self):
        """
        Start a while loop that collects all the block data
        based on the config values
        """
        # Connect to Kafka
        await self.kafka_manager.start()

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
            await self.kafka_manager.send_message("test")
            break

        await self.kafka_manager.stop()
