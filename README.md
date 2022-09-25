# Blockchain data collection and processing

## Overview
The app consists of four main components:
  * Data producer - scrape block data from the nodes and propagate to a message queue
  * Data consumer - save data from transactions to the database
  * Message queue - Kafka
  * Database - PostgreSQL

![App overview](etc/img/overview.png)

The block / transaction consumers are blockchain agnostic / evm compatible, thus only require a configuration file to specify which blockchain should be mined for data and stored later.

### Directory structure
```
.
├── README.md
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.yml
├── etc                         # utility files
│   ├── img
│   └── scripts                 # scripts for running the app
└── src                         # source code for containers
    ├── data_collection         # producer + consumer code
    └── db
.
├── README.md
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.tests.yml
├── docker-compose.yml
├── etc
│   ├── img
│   ├── scripts                 # scripts for running app and tests
│   └── web3_examples.ipynb
└── src                         # code for containers / services
    ├── data_collection         # producer + consumer code
    ├── db                      # dataschema definitions
    └── kafka
```

## Running the app
The application stack is managed by [docker compose](https://docs.docker.com/compose/#compose-v2-and-the-new-docker-compose-command). Each compose configuration file targets a different environment.

## Configuration

The main configuration files are located in `etc/cfg` and are split between a development and production enviornment.

The only environment variable is `LOG_LEVEL` which you can freely set in the docker-compose. The default value is set in `src/data_collection/Dockerfile` as `INFO`

### Development environment
The development environment build is intended for development purposes. It creates a local PostgreSQL database (with persistence in `src/sql/db-data`) and connects to public blockchain node APIs such as Infura.

To run a development build:
```
$ sh scripts/run-dev.sh
```

#### Per node dev config
You can also run the app only for a specific blockchain.
```
# ETH
$ sh scripts/run-dev-eth.sh
# ETC
$ sh scripts/run-dev-etc.sh
# BSC
$ sh scripts/run-dev-bsc.sh
```

### Production environment
The production environment build expects a database / local blockchain nodes to be already reachable.

To run a production build:
```
$ sh scripts/run-prod.sh
```

> Note: If you encounter a `Error response from daemon: network` error, the volumes need to be fully restarted with `docker compose down --volumes --remove-orphans`.

## Running only the database
In case you only need to run the development database:
```
$ sh scripts/run-dev-db.sh
```

For connecting to the database check [src/db/README.md](src/db/README.md).

## Tests

Currently, only the `DatabaseManager` class is tested. These database manager tests require an active database connection so the configuration in `docker-compose.tests.yml` starts an in-memory postgresql database along with the testing container.

To start the tests:
```
$ sh scripts/run-tests-db.sh
```

> Note: When running the tests locally, it might sometimes be necessary to `docker volume prune` in order for the database to restart properly.
