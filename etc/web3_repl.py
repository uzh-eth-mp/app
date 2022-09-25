import json

from web3 import Web3
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import (
    Geth,
    AsyncGethTxPool,
    AsyncGethAdmin,
    AsyncGethPersonal
)
from web3.exceptions import ABIFunctionNotFound

#node_url = "http://localhost:8545"
node_url = "https://mainnet.infura.io/v3/5ac780e50f2d4c48aedf160d077963ce"
usdt_contract_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
bayc_contract_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
erc1155_contract_address = "0x9cA3A9a3aA59C7ddd61C29f6b0540ad9988AeDE6"

w3 = Web3(
    provider=Web3.AsyncHTTPProvider(node_url),
    modules={
        "eth": (AsyncEth,),
        "net": (AsyncNet,),
        "geth": (Geth, {
            "txpool": (AsyncGethTxPool,),
            "perosnal": (AsyncGethPersonal,),
            "admin": (AsyncGethAdmin,)
        })
    },
    middlewares=[]
)

abi_json = json.load(open("src/data_collection/etc/abi.json"))

import asyncio
from eth_hash.auto import keccak

async def has_function(contract_address, fn_signature: str) -> bool:
    """Check if a contract contains a function signature"""
    code = (await w3.eth.get_code(contract_address)).hex()
    fn_hash = keccak(fn_signature.encode()).hex()
    fn_hash = f"63{fn_hash[:8]}"
    return fn_hash in code

async def parse_erc20(abi):
    contract = w3.eth.contract(
        address=usdt_contract_address,
        abi=abi
    )
    symbol = await contract.functions.symbol().call()
    name = await contract.functions.name().call()
    decimals = await contract.functions.decimals().call()
    total_supply = await contract.functions.totalSupply().call()

    return

async def test(contract_address):
    is_erc20 = \
        await has_function(contract_address, "transfer(address,uint256)") and \
        await has_function(contract_address, "transferFrom(address,address,uint256)")
    is_erc721 = \
        not await has_function(contract_address, "transfer(address,uint256)") and \
        await has_function(contract_address, "transferFrom(address,address,uint256)")
    is_erc1155 = await has_function(
        contract_address,
        "safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)"
    )
    print(f"{is_erc20} {is_erc721} {is_erc1155}")

asyncio.run(test(erc1155_contract_address))
