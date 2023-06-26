# Example

This document shows an example of a simple configuration, orchestration and the output of running the application stack in both environments.

This example will:
* start 1 producer that will insert all transactions into Kafka in the block range 13000000-13000020
* start 2 consumers that will consume all transactions from Kafka and only save data for those that are related to USDT and contain a Transfer event in the logs
* stop all containers after 10 minutes of no events received from Kafka in all consumers.

## Configuration
Use the same configuration as shown in [docs/configuration.md](/docs/configuration.md#cfgjson). You may only need to adjust the `node_url`.

Copy this configuration into [src/data_collection/etc/cfg/dev/eth.json](/src/data_collection/etc/cfg/dev/eth.json).

Make sure to also have an `.env` file in the root of the repository (`cp .env.default .env`)

## Running in development mode


## Running in production mode
