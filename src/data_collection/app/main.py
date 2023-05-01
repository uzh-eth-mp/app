import argparse
import asyncio
import sys

import uvloop
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration

from app import init_logger
from app.config import Config
from app.producer import DataProducer
from app.consumer import DataConsumer
from app.utils.enum_action import EnumAction
from app.model import DataCollectionMode
from app.model.abi import ContractABI


log = init_logger(__name__)


async def main(args: argparse.Namespace, config: Config):
    app_name = f"{args.mode.value}-{config.kafka_topic}"

    log.info(f"Starting {app_name}")
    exit_code = 0

    # Start the app in the correct mode
    if args.mode == DataCollectionMode.CONSUMER:
        # Load the ABIs
        contract_abi = ContractABI.parse_file(args.abi_file)
        consumer_tasks = []

        # Consumer
        async def start_consumer():
            async with DataConsumer(config, contract_abi) as data_consumer:
                await data_consumer.start_consuming_data()

        # Start N_CONSUMER_INSTANCES asyncio tasks
        for _ in range(config.number_of_consumer_tasks):
            # TODO: # of consumers can be increased by using a asyncpg connection_pool across
            # all the tasks within this process
            consumer_tasks.append(asyncio.create_task(start_consumer()))
        result = await asyncio.gather(*consumer_tasks)
        # Return erroneous exit code if needed
        exit_code = int(any(result))
    elif args.mode == DataCollectionMode.PRODUCER:
        # Producer
        async with DataProducer(config) as data_producer:
            exit_code = await data_producer.start_producing_data()

    log.info(f"Exiting {app_name} with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    # CLI arguments parser
    parser = argparse.ArgumentParser(description="EVM-node Data Collector")
    parser.add_argument(
        "--cfg", help="The configuration file path", type=str, required=True
    )
    parser.add_argument(
        "--abi-file",
        help="The path to a file that contains ERC ABIs",
        type=str,
        default="etc/contract_abi.json",
    )
    parser.add_argument(
        "--mode",
        help="The data collection mode (producing or consuming data)",
        type=DataCollectionMode,
        action=EnumAction,
        required=True,
    )
    args = parser.parse_args()

    # Load the config file
    config: Config = Config.parse_file(args.cfg)

    # Initialize Sentry if needed (env var SENTRY_DSN present)
    if sentry_dsn := config.sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                AsyncioIntegration(),
            ],
        )

    # Run the app
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        runner.run(main(args, config))
