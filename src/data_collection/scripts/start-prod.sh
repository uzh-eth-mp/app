#!/bin/sh

sleep 5

cat /etc/hosts

curl --head --connect-timeout 3 erigon_proxy:18547

python3 -m app.main --cfg etc/cfg/prod/eth.json --mode producer