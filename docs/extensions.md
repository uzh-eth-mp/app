# Extensions
## Add new Event

1. Define the event class in [app](/src/data_collection/app/web3/transaction_events/types.py) 
  * (e.g. for the `MintFungibleEvent`)
  ```
  class MintFungibleEvent(ContractEvent):
    """
    This represents mint event.
    """

    value: int

  ```

2. Add an instance of the event in [app](/src/data_collection/app/consumer/tx_processor.py) to the `_handle_transaction_events()` function 
  * (e.g. here the elif clause for the MintFungibleEvent)
  ```
  async def _handle_transaction_events(
        self,
        contract: Contract,
        category: ContractCategory,
        tx_data: TransactionData,
        tx_receipt: TxReceipt,
    ) -> Set[int]:
        """Insert transaction events (supply changes) into the database

        Returns:
            log_indices_to_save: a set of 'logIndex' for logs that should be saved
        """
        ....
 
        for event in get_transaction_events(category, contract, tx_receipt):
            ...

            if isinstance(event, BurnFungibleEvent):
                amount_changed -= event.value
            elif isinstance(event, MintFungibleEvent):
                amount_changed += event.value
  ```
  3. Map the event to a contract in [app](/src/data_collection/app/web3/transaction_events)
    * (e.g. MintfungibleEvent is mapped to a erc20 token in [app](/src/data_collection/app/web3/transaction_events/erc20.py))
    ```
    @_event_mapper(ContractCategory.ERC20)
    def _issue(contract: Contract, receipt: TxReceipt) -> EventsGenerator:
    ...
    for eventLog in contract.events.Issue().process_receipt(receipt, errors=DISCARD):
        val = eventLog["args"]["amount"]
        address = eventLog["address"]
        log_index = eventLog["logIndex"]
        yield MintFungibleEvent(
            address=address,
            log_index=log_index,
            value=val,
        )
    ```

  4. Add test in [app](/src/data_collection/tests/unit/web3/test_transaction_events.py) if needed

## Add new Contract ABI

In order to extend the application with a new token contract the following steps have to be considered: 

1. Add new Contract Application Binary Interface (ABI) for the specific token in JSON format to [app](/src/data_collection/etc/contract_abi.json). 

2. Update in [app](/src/data_collection/app/model/abi.py) the `ContractABI(BaseModel)` class
  * (e.g.for erc20 Token)
   ```
   class ContractABI(BaseModel):
      """Model for Contract ABIs. The data is loaded from `abi.json`"""

      erc20: List[Dict[str, Any]]

    ```

3. Add contract category enum value to the `ContractCategory(Enum)` [app](/src/data_collection/app/model/contract.py) class.

4. Update the [app](/src/data_collection/app/web3/parser.py) class 
  * Add an elif clause for the added Token to the `_get_contract_abi()` function:
     ```
    def _get_contract_abi(
        self, contract_category: ContractCategory
    ) -> Optional[List[Dict[str, Any]]]:
        """Return contract ABI depending on the contract category"""
        abi = None
        if contract_category == ContractCategory.BEP20:
            api = self.contract_abi.bep20
        elif contract_category == ContractCategory.ERC20:
            abi = self.contract_abi.erc20
        elif contract_category == ContractCategory.ERC721:
     ```
  * If the added contract is a token contract (i.e erc20, bep20) a category can be added in the `get_token_contract_data()` function and if the contract is a pair contract (i.e. Uniswap) the category can be added in the `get_pair_contract_data()` function. 
 

## Add new data collection mode

Adding a new data collection / processing mode can be useful if you want to make use of parallelization via Kafka workers. This is an example on how we added the `get_logs` data collection mode.

1. Add new `DataCollectionMode` enum value in [app/model/__init__.py](/src/data_collection/app/model/__init__.py).
  * `GET_LOGS = auto()`
  * add documentation if needed
2. Update [app/config.py](/src/data_collection/app/config.py) if needed
  * (e.g. get_logs method requires 'params' field)
    ```
    class DataCollectionConfig(BaseSettings):
        ...
        params: Optional[Dict[str, Any]]
        """Can be none, required when used with DataCollectionMode.GET_LOGS

        Note:
            This field has to have the same JSON format as the eth_getLogs RPC method:
            https://www.quicknode.com/docs/ethereum/eth_getLogs
        """
    ```
3. Update [app/producer.py](/src/data_collection/app/producer.py) to account for the new `DataCollectionMode`
  * add new method `_start_get_logs_producer()` to `DataProducer`.
    ```
    async def _start_get_logs_producer(
        self, data_collection_cfg: DataCollectionConfig
    ):
        """Start a producer that uses the `eth_getLogs` RPC method to get all the transactions"""
    ```
  * add `match` case for the new `DataCollectionMode` in `_start_producer_task()` method:
    ```
    case DataCollectionMode.GET_LOGS:
        return asyncio.create_task(
            self._start_get_logs_producer(data_collection_cfg)
        )
    ```
  * implement `_start_get_logs_producer()`:
  * call `eth_getLogs` and then send all transactions to Kafka
    ```
        """Start a producer that uses the `eth_getLogs` RPC method to get all the transactions"""
        # Get logs
        logs = await self.node_connector.w3.eth.get_logs(filter_params=data_collection_cfg.params)

        # Send them to Kafka
        if logs:
            # Encode the logs as kafka events
            messages = [
                self.encode_kafka_event(log["transactionHash"].hex(), data_collection_cfg.mode)
                for log in logs
            ]
            # Send all the transaction hashes to Kafka so consumers can process them
            await self.kafka_manager.send_batch(msgs=messages)

        log.info(f"Finished collecting {len(logs)} logs")
    ```
4. (Optional) implement a new transaction processor for the new DataCollectionMode in [app/consumer/tx_processor.py](/src/data_collection/app/consumer/tx_processor.py)
  * Create new class for `GetLogsTransactionProcessor`
  * Update `self.tx_processors` in `DataConsumer` to use this new `GetLogsTransactionProcessor`
  ```
    self.tx_processors = {
        ...,
        DataCollectionMode.GET_LOGS: GetLogsTransactionProcessor(*_tx_processor_args)
    }
  ```
5. Update the JSON config and run the app

## Support more blockchains

In order to be able to support more Blockchains for the data collection the following configurations have to be added. 

1. Add `cfg.json` file [app](/src/data_collection/etc/cfg) in the following format: `<blockchain>.json`. The file can be copied from an existing Blockchain(i.e eth.json), the `node_url` has be changed to the new Blockchain url and the `contracts` which should to be collected in `partial` mode have to be added. The token category and events have to be added first as explained in the chapters above. 
 * i.e. for eth
  ```
  {
      "node_url": "http://host.docker.internal:8547",
      ....

      "data_collection": [
          {
              "mode": "partial",
              "start_block": 16804500,
              "end_block": 17100000,
              "contracts": [
                  {
                      "address": "0xED5AF388653567Af2F388E6224dC7C4b3241C544",
                      "symbol": "Azuki",
                      "category": "erc721",
                      "events": [
                          "TransferNonFungibleEvent"
                      ]
                  },
                  {
                      "address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
                      "symbol": "BAYC",
                      "category": "erc721",
                      "events": [
                          "TransferNonFungibleEvent"
                      ]
                  }, ...
    }
  ```

2. Update the `docker-compose-<environment>.yaml` in [app] and add an entry for a `data_producer_<blockchain>` and `data_consumer__<blockchain>` and update in the `command` field the --cfg flag to the file added in 1. 
  * i.e for eth: 
  ```
  data_producer_eth:
    environment:
      KAFKA_N_PARTITIONS: 4
    command: bash -c "bash wait-for-kafka.sh && python3 -m app.main --cfg etc/cfg/dev/eth.json --worker-type producer"

  data_consumer_eth:
    command: bash -c "bash wait-for-kafka.sh && python3 -m app.main --cfg etc/cfg/dev/eth.json --worker-type consumer"
    deploy:
      replicas: 2
    environment:
      KAFKA_N_PARTITIONS: 4
      N_CONSUMER_INSTANCES: 1
  ```

3. Add a new `run-<environment>-<blockchain>` script to [app](/scripts) and copy the code from the script of any other blockchain and update inside the file everywhere the name of the blockchain to the new one. 

4. Update the `ERIGON_PORT` in the `.env` file to the port of the new Blockchain.

5. Run the  new `run-<environment>-<blockchain>`script.
