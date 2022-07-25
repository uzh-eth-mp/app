import argparse
import asyncio

from app import init_logger
from app.config import Config
from app.consumer import DataConsumer


log = init_logger(__name__)

async def main(config: Config):
    log.info("Starting the app...")
    consumer = DataConsumer(config)
    await consumer.start_data_processing()
    log.info("Exiting the app...")


if __name__ == "__main__":
    # CLI arguments parser
    parser = argparse.ArgumentParser(description="Block Consumer")
    parser.add_argument(
        "--cfg",
        help="The configuration file path",
        type=str,
        required=True
    )
    args = parser.parse_args()

    # Load the config file
    config = Config.parse_file(args.cfg)
    log.info("Config loaded.")

    # Run the app
    asyncio.run(main(config))
