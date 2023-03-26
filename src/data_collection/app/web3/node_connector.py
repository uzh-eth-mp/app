from typing import Tuple

from web3 import Web3
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import (
    Geth,
    AsyncGethTxPool,
    AsyncGethAdmin,
    AsyncGethPersonal
)
from web3.types import TxData, TxReceipt

from app.model.block import BlockData
from app.model.transaction import (
    TransactionData,
    TransactionReceiptData,
    InternalTransactionData
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
        # Workaround with headers allows to connect to the Abacus
        # JSON RPC API through an SSH tunnel. Abacus only allows hostname to
        # be "localhost" otherwise it returns a 403 response code.
        headers = {
            "Host": "localhost",
            "Content-Type": "application/json"
        }
        self.w3 = Web3(
            provider=Web3.AsyncHTTPProvider(
                endpoint_uri=node_url,
                request_kwargs={
                    "headers": headers
                }
            ),
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

    async def get_block_data(self, block_id: str="latest") -> BlockData:
        """Get block data by number/hash"""
        block_data_dict = await self.w3.eth.get_block(block_id)
        block_data = BlockData(**block_data_dict, w3_data=block_data_dict)
        return block_data

    async def get_latest_block_number(self) -> int:
        """Get latest block number"""
        return await self.w3.eth.block_number

    async def get_transaction_data(self, tx_hash: str) -> Tuple[TransactionData, TxData]:
        """Get transaction data by hash

        Returns:
            tx_data (TransactionData)
            tx_data_dict (web3.TxData)
        """
        tx_data_dict = await self.w3.eth.get_transaction(tx_hash)
        tx_data = TransactionData(**tx_data_dict)
        return tx_data, tx_data_dict

    async def get_transaction_receipt_data(self, tx_hash: str) -> Tuple[TransactionReceiptData, TxReceipt]:
        """Get transaction receipt data by hash

        Returns:
            tx_receipt_data (TransactionReceiptData)
            tx_receipt_data_dict (web3.TxReceipt)
        """
        tx_receipt_data_dict = await self.w3.eth.get_transaction_receipt(tx_hash)
        tx_receipt_data = TransactionReceiptData(**tx_receipt_data_dict)
        return tx_receipt_data, tx_receipt_data_dict

    # TODO: finish get_internal_transactions
    async def get_internal_transactions(self, tx_hash: str) -> InternalTransactionData:
        """Get internal transaction data by hash"""
        pass
