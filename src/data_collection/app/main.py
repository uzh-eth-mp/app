import argparse
import asyncio

from app import init_logger
from app.config import Config
from app.producer import DataProducer
from app.consumer import DataConsumer
from app.utils.enum_action import EnumAction
from app.model import DataCollectionMode
from app.model.abi import ERCABI


log = init_logger(__name__)

async def main(args: argparse.Namespace):
    # Load the config file
    config: Config = Config.parse_file(args.cfg)
    app_name = f"{args.mode.value}-{config.kafka_topic}"

    log.info(f"Starting {app_name}")

    # Start the app in the correct mode
    if args.mode == DataCollectionMode.CONSUMER:
        # Load the ABIs
        erc_abi = ERCABI.parse_file(args.abi_file)
        # Consumer
        async with DataConsumer(config, erc_abi) as data_consumer:
            await data_consumer.start_consuming_data()
    elif args.mode == DataCollectionMode.PRODUCER:
        # Producer
        async with DataProducer(config) as data_producer:
            await data_producer.start_producing_data()

    log.info(f"Exiting {app_name}")


if __name__ == "__main__":
    # CLI arguments parser
    parser = argparse.ArgumentParser(description="EVM-node Data Collector")
    parser.add_argument(
        "--cfg",
        help="The configuration file path",
        type=str,
        required=True
    )
    parser.add_argument(
        "--abi-file",
        help="The path to a file that contains ERC ABIs",
        type=str,
        default="etc/abi.json"
    )
    parser.add_argument(
        "--mode",
        help="The data collection mode (producing or consuming data)",
        type=DataCollectionMode,
        action=EnumAction,
        required=True
    )
    args = parser.parse_args()

    # Run the app
    asyncio.run(main(args))
