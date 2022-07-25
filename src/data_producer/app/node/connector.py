from typing import Any

from web3 import Web3
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import (
    Geth,
    AsyncGethTxPool,
    AsyncGethAdmin,
    AsyncGethPersonal
)


class NodeConnector:
    """Connect to a blockchain node and scrape / mine data

    This class is responsible for all the web3 operations that
    are required by this app.
    """

    def __init__(self, node_url: str) -> None:
        """
        Args:
            node_url: the RPC API URL for connecting
                        to an EVM node
        """
        # Initialize an async web3 instance
        self.w3 = Web3(
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

    async def get_block_data(self, block_id="latest") -> dict[str, Any]:
        """Get block data by number/hash"""
        return await self.w3.eth.get_block(block_id)

    async def get_latest_block_number(self) -> int:
        """Get latest block number"""
        return await self.w3.eth.block_number