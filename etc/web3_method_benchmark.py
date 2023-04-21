from web3 import Web3
import time
import asyncio
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import Geth, AsyncGethTxPool, AsyncGethAdmin, AsyncGethPersonal

node_url = "http://localhost:8547"

headers = {
    "Host": "localhost",
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
}
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

N_REQUESTS = 1000


async def main(block_number):
    """
    Args:
        block_number: starting block number
    """
    request_time_getBlock = 0
    # keep a list of txs for later
    tx_hashes = []
    for i in range(N_REQUESTS):
        start = time.perf_counter()
        block_data = await w3.eth.get_block(block_number + i)
        if len(block_data["transactions"]) > 1 and len(tx_hashes) < N_REQUESTS:
            tx_hashes.append(block_data["transactions"][0])
            tx_hashes.append(block_data["transactions"][1])
        request_time_getBlock += time.perf_counter() - start

    print(f"Method get_block_data avg response time: {request_time_getBlock:.0f} ms")

    request_time_getTransaction = 0
    for i in range(N_REQUESTS):
        start = time.perf_counter()
        tx_data_dict = await w3.eth.get_transaction(tx_hashes[i])
        request_time_getTransaction += time.perf_counter() - start

    print(
        f"Method get_transaction_data avg response time: {request_time_getTransaction:.0f} ms"
    )

    request_time_internaltx = 0
    ii = 0
    for i in range(N_REQUESTS):
        """Get internal transaction data by hash"""
        ii = i
        start = time.perf_counter()
        data = await w3.provider.make_request(
            "trace_replayTransaction", [tx_hashes[i].hex(), ["trace"]]
        )
        request_time_internaltx += time.perf_counter() - start
    print(
        f"Method trace_replayTransaction avg response time: {request_time_internaltx:.0f} ms"
    )

    request_time_blockReward = 0
    for i in range(N_REQUESTS):
        start = time.perf_counter()
        data = await w3.provider.make_request("trace_block", [block_number + i])
        request_time_blockReward += time.perf_counter() - start

    print(f"Method trace_block avg response time: {request_time_blockReward:.0f} ms")


asyncio.run(main(15500000))
