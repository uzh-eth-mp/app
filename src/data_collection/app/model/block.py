from datetime import datetime
from typing import List

from pydantic import Field, validator

from app.model import Web3BaseModel 
from app.model import  convert_string_to_bytes



class BlockData(Web3BaseModel):
    """Describes a block given by `get_block`"""

    block_number: int = Field(..., alias="number")
    block_hash: bytes = Field(..., alias="hash")
    nonce: bytes
    difficulty: int
    gas_limit: int = Field(..., alias="gasLimit")
    gas_used: int = Field(..., alias="gasUsed")
    timestamp: datetime
    transactions: List[bytes]
    miner: bytes
    parent_hash: bytes = Field(..., alias="parentHash")
    uncles: List[bytes]


    @validator("timestamp", pre=True)
    def timestamp_to_datetime(cls, v):
        """Integer timestamp to datetime.datetime validator"""
        return datetime.fromtimestamp(v)
    
    _convert_hexstr_to_bytea = validator("block_hash", "nonce", "miner", "parent_hash"
    , allow_reuse=True)(convert_string_to_bytes) 

    _convert_list_hexstr_to_bytea = validator("transactions", "uncles", allow_reuse=True, each_item=True)
    (convert_string_to_bytes) 
