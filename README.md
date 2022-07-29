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
```

## Running the app
The application stack is managed by docker-compose. Each compose configuration file targets a different environment.

### Development
The development build creates a local PostgreSQL database and connects to public blockchain node APIs.

To run a development build:
```
$ sh etc/scripts/run-dev.sh
```

#### Per node dev config
You can also run the app only for a specific blockchain.
```
# ETH
$ sh etc/scripts/run-dev-eth.sh
# ETC
$ sh etc/scripts/run-dev-etc.sh
# BSC
$ sh etc/scripts/run-dev-bsc.sh

```

### Production
The production build expects a database / local blockchain nodes to be already reachable.

To run a production build:
```
$ sh etc/scripts/run-prod.sh
```

> Note: If you encounter a `Error response from daemon: network` error, the volumes need to be fully restarted with `docker-compose down --volumes --remove-orphans`.

## Running only the database
In case you only need to run the development database:
```
$ sh etc/scripts/run-dev-db.sh
```

For connecting to the database check [src/db/README.md](src/db/README.md).