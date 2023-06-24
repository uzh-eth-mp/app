from typing import List, Optional

from pydantic import Field, validator

from app.model import Web3BaseModel , convert_string_to_bytes


class TransactionData(Web3BaseModel):
    """Describes a transaction given by `get_transaction`"""

    transaction_hash: Optional[bytes] = Field(None, alias="hash")
    block_number: Optional[int] = Field(None, alias="blockNumber")
    from_address: Optional[bytes] = Field(None, alias="from")
    to_address: Optional[bytes] = Field(None, alias="to")
    value: Optional[float] = None
    gas_price: Optional[float] = Field(None, alias="gasPrice")
    gas_limit: Optional[float] = Field(None, alias="gas")
    input_data: Optional[bytes] = Field(None, alias="input")

    _convert_hexstr_to_bytea = validator("transaction_hash", "from_address", "to_address", "input_data"
    , allow_reuse=True)(convert_string_to_bytes) 

class TransactionLogsData(Web3BaseModel):
    """Describes transaction receipt logs given by `get_transaction_receipt`"""

    address: Optional[bytes] = None
    data: Optional[bytes] = None
    removed: Optional[bool] = None
    topics: Optional[List[bytes]] = None
    log_index: Optional[int] = Field(None, alias="logIndex")
    transaction_hash: Optional[bytes] = Field(None, alias="transactionHash")

    _convert_hexstr_to_bytea = validator("address", "data", "transaction_hash",
     allow_reuse=True)(convert_string_to_bytes) 

    _convert_list_hexstr_to_bytea = validator("topics", allow_reuse=True, each_item=True)
    (convert_string_to_bytes) 


class TransactionReceiptData(Web3BaseModel):
    """Describes a transaction receipt given by `get_transaction_receipt`"""

    gas_used: Optional[float] = Field(None, alias="gasUsed")
    logs: Optional[List[TransactionLogsData]] = None
    transaction_type: bytes = Field(None, alias="type")
    contract_address: Optional[bytes] = Field(None, alias="contractAddress")

    _convert_hexstr_to_bytea = validator("transaction_type", "contract_address"
    , allow_reuse=True)(convert_string_to_bytes)

class InternalTransactionData(Web3BaseModel):
    """Describes an internal transaction given by `debug_traceTransaction`"""

    from_address: Optional[bytes] = Field(None, alias="from")
    to_address: Optional[bytes] = Field(None, alias="to")
    value: Optional[float] = None
    gas_used: Optional[float] = Field(None, alias="gasUsed")
    gas_limit: Optional[float] = Field(None, alias="gas")
    input_data: Optional[bytes] = Field(None, alias="input")
    call_type: Optional[bytes] = Field(None, alias="callType")

    @validator("value", "gas_used", "gas_limit", pre=True)
    def strings_to_float(cls, v):
        return float.fromhex(v)
        
    _convert_hexstr_to_bytea = validator("from_address", "to_address", "input_data", "call_type"
    , allow_reuse=True)(convert_string_to_bytes) 