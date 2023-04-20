import json

from web3 import Web3
import time
import asyncio
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import Geth, AsyncGethTxPool, AsyncGethAdmin, AsyncGethPersonal
from web3.exceptions import ABIFunctionNotFound

node_url = "http://localhost:8547"
# node_url = "https://mainnet.infura.io/v3/5ac780e50f2d4c48aedf160d077963ce"
usdt_contract_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
bayc_contract_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
erc1155_contract_address = "0x9cA3A9a3aA59C7ddd61C29f6b0540ad9988AeDE6"

headers = {"Host": "localhost", "Content-Type": "application/json"}
w3 = Web3(
    provider=Web3.AsyncHTTPProvider(
        endpoint_uri=node_url, request_kwargs={"headers": headers}
    ),
    modules={
        "eth": (AsyncEth,),
        "net": (AsyncNet,),
        "geth": (
            Geth,
            {
                "txpool": (AsyncGethTxPool,),
                "perosnal": (AsyncGethPersonal,),
                "admin": (AsyncGethAdmin,),
            },
        ),
    },
    middlewares=[],
)

block_numbers = ["15500000","15500001","15500002", "15500003"]
tx_hashes = ["0xc38b00f67245dd8bd43a0f125143e958e776a3db01c20cf85e3a31daa56ecb6c","0xe15919bc23b93fdb6ea6c5cfb5946791922c32ce85deed581f63d045bffc9395",
"0x68469a8d5af166547bdf050c2a055b4ec4b31896e61c16d451d4df79e19e2dfd","0xcf766d4645936f062f9b8cec0da34699d32c19e35eac67322c935dc8535637e5"]

async def main(block_number, tx_hash):
    request_time_getBlock = 0
    for i in range(1000): 
        start = time.perf_counter()
        block_data = await w3.eth.get_block(block_number)
        request_time_getBlock += time.perf_counter() - start

    print("Method get_block_data avg time:",request_time_getBlock/1000)

    
    request_time_getTransaction = 0
    for i in range(1000): 
        start = time.perf_counter()
        tx_data_dict = await w3.eth.get_transaction(tx_hash)
        request_time_getTransaction = time.perf_counter() - start
    
    print("Method get_transaction_data avg time:", request_time_getTransaction/1000)


    request_time_internaltx = 0
    for i in range(1000):
        """Get internal transaction data by hash"""
        start = time.perf_counter()
        data = await w3.provider.make_request(
            "trace_replayTransaction", [tx_hash, ["trace"]]
        )
        request_time_internaltx = time.perf_counter() - start
    
    print("Method trace_replayTransaction avg time:", request_time_internaltx/1000)


    request_time_blockReward = 0
    for i in range(1000):
        start = time.perf_counter()
        data = await w3.provider.make_request("trace_block", [block_number])
        request_time_blockReward = time.perf_counter() - start     
    
    print("Method trace_block avg time:",request_time_blockReward/1000)


asyncio.run(main("15500000","0xc38b00f67245dd8bd43a0f125143e958e776a3db01c20cf85e3a31daa56ecb6c"))

    