from typing import List, Optional

from pydantic import Field

from app.model import Web3BaseModel, convert_string_to_bytes

from pydantic import Field, validator


class TransactionData(Web3BaseModel):
    """Describes a transaction given by `get_transaction`"""

    transaction_hash: bytes = Field(..., alias="hash")
    block_number: int = Field(..., alias="blockNumber")
    from_address: bytes = Field(..., alias="from")
    to_address: Optional[bytes] = Field(..., alias="to")
    value: float
    gas_price: float = Field(..., alias="gasPrice")
    gas_limit: float = Field(..., alias="gas")
    input_data: bytes = Field(..., alias="input")

    _convert_hexstr_to_bytea = validator("transaction_hash", "from_address", "to_address", "input_data"
    , allow_reuse=True)(convert_string_to_bytes) 




class TransactionLogsData(Web3BaseModel):
    """Describes transaction receipt logs given by `get_transaction_receipt`"""

    address: bytes
    data: bytes
    removed: bool
    topics: List[bytes]
    log_index: int = Field(..., alias="logIndex")
    transaction_hash: bytes = Field(..., alias="transactionHash")

    _convert_hexstr_to_bytea = validator("address", "data", "transaction_hash",
     allow_reuse=True)(convert_string_to_bytes) 

    _convert_list_hexstr_to_bytea = validator("topics", allow_reuse=True, each_item=True)
    (convert_string_to_bytes) 
    


class TransactionReceiptData(Web3BaseModel):
    """Describes a transaction receipt given by `get_transaction_receipt`"""

    gas_used: float = Field(..., alias="gasUsed")
    logs: List[TransactionLogsData]
    transaction_type: bytes = Field(..., alias="type")
    contract_address: Optional[bytes] = Field(..., alias="contractAddress")

    _convert_hexstr_to_bytea = validator("transaction_type", "contract_address"
    , allow_reuse=True)(convert_string_to_bytes) 


class InternalTransactionData(Web3BaseModel):
    """Describes an internal transaction given by `debug_traceTransaction`"""

    from_address: bytes = Field(..., alias="from")
    to_address: Optional[bytes] = Field(..., alias="to")
    value: float
    gas_used: Optional[float] = Field(None, alias="gasUsed")
    gas_limit: float = Field(..., alias="gas")
    input_data: Optional[bytes] = Field(..., alias="input")
    call_type: Optional[bytes] = Field(..., alias="callType")

    @validator("value", "gas_used", "gas_limit", pre=True)
    def strings_to_float(cls, v):
        return float.fromhex(v)

    _convert_hexstr_to_bytea = validator("from_address", "to_address", "input_data", "call_type"
    , allow_reuse=True)(convert_string_to_bytes) 

