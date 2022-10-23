from typing import List, Optional

from pydantic import Field
from web3.types import TxData, TxReceipt

from app.model import Web3BaseModel


class TransactionData(Web3BaseModel):
    """Describes a transaction given by `get_transaction`"""
    transaction_hash: str = Field(..., alias="hash")
    block_number: int = Field(..., alias="blockNumber")
    block_hash: str = Field(..., alias="blockHash")
    from_address: str = Field(..., alias="from")
    to_address: Optional[str] = Field(..., alias="to")
    value: float
    gas_price: float = Field(..., alias="gasPrice")
    gas_limit: float = Field(..., alias="gas")
    input_data: str = Field(..., alias="input")
    _w3_data: TxData
    class Config:
        arbitrary_types_allowed = True


class TransactionLogsData(Web3BaseModel):
    """Describes transaction receipt logs given by `get_transaction_receipt`"""
    address: str
    data: str
    removed: bool
    topics: List[str]
    log_index: int = Field(..., alias="logIndex")
    transaction_hash: str = Field(..., alias="transactionHash")


class TransactionReceiptData(Web3BaseModel):
    """Describes a transaction receipt given by `get_transaction_receipt`"""
    gas_used: float = Field(..., alias="gasUsed")
    logs: List[TransactionLogsData]
    transaction_type: str = Field(..., alias="type")
    contract_address: Optional[str] = Field(..., alias="contractAddress")
    w3_data: TxReceipt
    class Config:
        arbitrary_types_allowed = True


# TODO: finish InternalTransactionData
class InternalTransactionData(Web3BaseModel):
    """Describes an internal transaction given by `debug_traceTransaction`"""
    pass
