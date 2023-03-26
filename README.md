# Blockchain data collection and processing

## Overview
The app consists of four main components:
  * Data producer - scrape block data from the node and propagate transactions to a message queue
  * Data consumer - save relevant transactions to the database
  * Message queue - Kafka
  * Database - PostgreSQL

![App overview](etc/img/overview.png)

Consumers are blockchain agnostic (EVM compatible), thus only require a configuration file to specify which blockchain should be mined for data and stored later.

### Directory structure
```
.
├── README.md
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.tests.yml
├── docker-compose.yml
├── etc                         # misc. files and images
│   └── img
├── scripts                     # scripts for running the stack and tests
└── src                         # code for containers / services
    ├── data_collection         # producer + consumer code
    ├── db                      # dataschema definitions
    ├── erigon_proxy            # reverse proxy service for accessing nodes
    ├── kafka                   # kafka setup code
    └── zookeeper               # kafka orchestration service
```

## Running the stack
The application stack is managed by [docker compose](https://docs.docker.com/compose/#compose-v2-and-the-new-docker-compose-command). Each compose configuration file targets a different environment (dev, prod, tests).

> App has been tested on `Docker Compose version v2.14.0`.

These compose files were intended to be ran by a run script which can be found in `scripts/`.

### Configuration
Two main configuration files need to be updated accordingly to your use case.
1. `.env` = most of the general variables
2. `src/data_collection/etc/cfg/<environment>/<blockchain>.json` = data collection, environment and blockchain specific settings

#### .env
To create an `.env` file you can copy the provided `.env.default` and edit the values as needed. The values in the `.env` file and their description:
| ENV_VAR | Description | Default value |
|---|---|---|
| `PROJECT_NAME` | Prefix for docker network and container names | "bdc" |
| `DATA_DIR` | Destination directory for the data (PostgreSQL, Kafka, Zookeeper) | "/local/scratch/bdc/data" |
| `LOG_LEVEL` | logging level of consumers and producers | "DEBUG" |
| `DATA_UID` | Data directory owner ID (can be left blank) | `id -u` |
| `DATA_GID` | Data directory owner group ID (can be left blank) | `getent group bdlt \| cut -d: -f3` |
| `POSTGRES_PORT` | Published host port for PostgreSQL | 13338 |
| `POSTGRES_USER` | Username for connecting to PostgreSQL service | "username" |
| `POSTGRES_PASSWORD` | Password for connecting to PostgreSQL service | "postgres" |
| `POSTGRES_DB` | PostgreSQL default database | "db" |
| `KAFKA_N_PARTITIONS` | The number of partitions per topic | 100 |
| `ERIGON_PORT` | Port of the erigon node | 8547 |
| `ERIGON_HOST` | Host of the erigon node | "host.docker.internal" |

#### cfg.json
FIXME: finish this section after adding "producer_type" for `config.py`

#### Additional configuration
On top of these configuration files, the application stack can be ran simultaneously for multiple blockchains (or individually). This functionality is achieved via [`profiles`](https://docs.docker.com/compose/profiles/) in `docker compose`.

For example, running the app for specific blockchain can be achieved via
```
# ETH
$ bash scripts/run-prod-eth.sh
# ETC
$ bash scripts/run-prod-etc.sh
# BSC
$ bash scripts/run-prod-bsc.sh
```

### Environment
#### Development environment
The development environment build is intended for development purposes. It creates a local PostgreSQL database (with persistence in `src/sql/db-data`) and connects to public blockchain node APIs such as Infura.

To run a development build:
```
$ sh scripts/run-dev.sh
```

#### Production environment
The production environment build expects a database / local blockchain nodes to be already reachable.

To run a production build:
```
$ bash scripts/run-prod.sh
```

> Note: If you encounter a `Error response from daemon: network` error, the volumes need to be fully restarted with `docker compose down --volumes --remove-orphans`.

## Running only the database
In case you only need to run the database, use:
```
$ sh scripts/run-db.sh
```

This script will only start the database service (defined in [docker-compose.yml](docker-compose.yml)) as a standalone container.

For connecting to the database check [src/db/README.md](src/db/README.md).

## Tests

Currently, only the `DatabaseManager` class is tested. These database manager tests require an active database connection so the configuration in `docker-compose.tests.yml` starts an in-memory postgresql database along with the testing container.

To start the tests:
```
$ sh scripts/run-tests-db.sh
```

> Note: When running the tests locally, it might sometimes be necessary to `docker volume prune` in order for the database to restart properly.

## TLDR / FAQ
* How do I start this *locally*?
  1. configure `.env`
  2. configure `src/data_collection/etc/cfg/dev/<blockchain>.json` (depending on your blockchain)
  3. run `bash scripts/run-dev-<blockchain>.sh`
* How do I start this on **Abacus-3**?
  1. configure `.env`
  2. configure `src/data_collection/etc/cfg/prod/<blockchain>.json` (depending on your blockchain)
  3. run `bash scripts/run-prod-<blockchain>.sh`
* How many topics and consumers should I use?
  * Depends on the machine you're running on, but generally the more consumers and topics, the faster the processing.
* Why am I seeing `Unable connect to "kafka:9092": [Errno 111] Connect call failed ('<container_ip>', 9092)` in the logs?
  * The producers and consumers attempt to connect to the Kafka container as soon as they're started. However the Kafka container takes some time. These messages are generated by the internal kafka library that is used within the project and can be ignored.
