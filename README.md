# EVM-compatible blockchain data collection

[![Unit tests](https://github.com/uzh-eth-mp/app/actions/workflows/test-unit.yaml/badge.svg?branch=dev)](https://github.com/uzh-eth-mp/app/actions/workflows/test-unit.yaml?query=branch%3Adev)
[![Integration tests](https://github.com/uzh-eth-mp/app/actions/workflows/test-database.yaml/badge.svg?branch=dev)](https://github.com/uzh-eth-mp/app/actions/workflows/test-database.yaml?query=branch%3Adev)
[![Docs](https://img.shields.io/readthedocs/handsdown.svg?color=blue&style=flat)](https://handsdown.readthedocs.io/)
[![Release](https://img.shields.io/github/v/release/uzh-eth-mp/app?style=flat)](https://github.com/uzh-eth-mp/app/releases/)


A collection of Docker Containers and their orchestration for collecting EVM-compatible blockchains' data.

* [Overview](#overview)
* [Directory Structure](#directory-structure)
* [Usage](#usage)
  * [Requirements](#requirements)
  * [Quickstart](#quickstart)
  * [Deployment Environment](#deployment-environment)
  * [Configuration](#configuration)
  * [Scripts](#scripts)
  * [Extensions](#extensions)
  * [Querying data](#querying-data)
  * [Tools](#tools)
* [FAQ](docs/faq.md)
* [Contributing](docs/contributing.md)

## Overview

![App overview](etc/img/overview.svg)

Main components (Docker containers):
  * Producer - scrape block data from the node and propagate transactions to Kafka
  * Consumers - save relevant transaction data to the database
  * Kafka - event store for transaction hashes
  * PostgreSQL - persistent data store
  * Redis - cache for orchestration data between producer and consumers

## Directory structure
```
./
├── etc/                      # misc. files
├── scripts/                  # bash scripts for orchestrating containers
├── src/                      # code for containers
│   ├── data_collection/      # producer + consumer
│   ├── db/                   # postgresql
│   ├── kafka/
│   └── zookeeper/
├── README.md
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.tests.yml
└── docker-compose.yml
```

## Usage
The containers are orchestrated by docker compose yaml files. For convenience a set of bash scripts has been provided for easily running the data collection process.

### Requirements
* [`docker compose`](https://docs.docker.com/compose/#compose-v2-and-the-new-docker-compose-command) (v2.14.0+)
  * to use with abacus-3: [install the compose plugin manually](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually).

### Quickstart
Compose files should be started with run scripts that can be found in the `scripts/` directory. For this you also need to have an `.env` file present. If you are cloning this directory, use `cp .env.default .env` and check all the env variables. Then:
```
$ bash scripts/run-prod-eth.sh
```

### Deployment Environment
There are two deployment environments available for the collection process.
* Development = use for development of new features
  * `$ bash scripts/run-dev.sh`
* Production = intended for use on Abacus-3, for long running collection of data
  * `$ bash scripts/run-prod.sh`

Each of these environments has their own configuration `.json` files. For instance, for *development* you would find the configuration files in [`src/data_collection/etc/cfg/dev`](src/data_collection/etc/cfg/dev/). Similarly, the *production* environment config is in [`src/data_collection/etc/cfg/prod`](src/data_collection/etc/cfg/prod/).
There is a minor difference between a development and production environment besides the configuration files, details can be found in the [scripts directory](scripts/README.md).

### Configuration
Two main configuration sources (files):
1. `.env` = static configuration variables (connection URLs, credentials, timeout settings, ...)
2. `src/data_collection/etc/cfg/<environment>/<blockchain>.json` = data collection configuration (block range, addresses, events)

The exact description of the environment variables and data collection configuration can be found [here](docs/configuration.md).
### Scripts
The scripts directory contains useful bash scripts that mostly consist of docker compose commands. Their detailed description can be found [here](scripts/README.md).
### Extensions
If you'd like to extend the current data collection functionality, such as:
* adding a new web3 `Event` to store in the db or to process (e.g. [OwnershipTransferred](https://docs.openzeppelin.com/contracts/2.x/api/ownership#Ownable-OwnershipTransferred-address-address-))
* adding a new contract ABI (e.g. [cETH](https://compound.finance/Developers/abi/mainnet/cETH))
* adding a new data collection mode (e.g. LogFilter)
* supporting more blockchains than ETH and BSC

Please check out the [functionality extension guide](docs/extensions.md).

### Querying Data
To query the collected data you will need a running PostgreSQL service:
```
$ bash scripts/run-db.sh
```

In order to then connect to the database, use:
```
$ docker exec -it bdc-db-1 psql <postgresql_dsn>
```
More details on how to connect can be found in the [src/db/](src/db/README.md) directory.


### Tools
The [etc/](etc/) directory contains a few python scripts that can be used for various tasks:
1. [get_top_uniswap_pairs.py](etc/get_top_uniswap_pairs.py) = print top `n` uniswap pairs in a JSON format ready to be plugged into the data collection cfg.json
2. [query_tool.py](etc/query_tool.py) = CLI with predefined SQL queries for easily accessing the DB.
3. [web3_method_benchmark.py](etc/web3_method_benchmark.py) = request response time benchmarking tool

## FAQ
A list of frequently asked questions and their answers can be found [here](docs/faq.md).

## Contributing
Contributions are welcome and appreciated. Please follow the convention and rules described [here](docs/contributing.md).

