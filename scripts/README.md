# Scripts

The following directory contains various scripts for running and testing the stack.

## Differences between Prod and Dev

1. Script exit
  * Production run script (`run-prod-eth.sh`) doesn't stop the containers on exit. For that you need to use `stop-prod-eth.sh`.
  * Dev run script (`run-dev-eth.sh`) stops (cleans up) all containers on `KeyboardInterrupt` or any other exit signal.
2. Environment Variables
  *

The [run-dev-eth.sh](scripts/run-dev-eth.sh) can be adapted for other blockchains by changing the compose profile and logs targets.

E.g. to create a `scripts/run-dev-bsc.sh` one would need to edit:
```
    # L20
    --profile eth up \
    # to
    --profile bsc up \

    # L26
    -f data_producer_eth data_consumer_eth
    # to
    -f data_producer_bsc data_consumer_bsc
```
