from app.web3.transaction_events import get_transaction_events
from app.web3.node_connector import NodeConnector
from app.model.abi import ContractABI
from app.web3.parser import ContractParser
from web3.contract import Contract
from web3.types import TxReceipt, HexBytes
from app.config import Config

erigon = NodeConnector(
    node_url="http://192.168.178.100:8545", # DO NOT MERGE, this is home erigon
    # Use this instead:
    # node_url=config.node_url,
    timeout=10, 
    retry_limit=2,  
    retry_delay=10)
contract_parser = ContractParser(
            web3=erigon.w3,
            contract_abi=ContractABI.parse_file("etc/contract_abi.json"),
            contracts={_ for cfg in Config.parse_file("etc/cfg/prod/eth.json").data_collection for _ in cfg.contracts},
        )


async def get_events(tx_hash, contract_address):
    _, tx_data = await erigon.get_transaction_data(tx_hash)
    _, tx_receipt = await erigon.get_transaction_receipt_data(tx_hash)

    category = contract_parser.get_contract_category(contract_address)
    contract = contract_parser.get_contract(contract_address=contract_address, category=category)
    return get_transaction_events(category, contract, tx_receipt, tx_data["blockHash"])