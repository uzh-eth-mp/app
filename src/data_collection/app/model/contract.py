from typing import Optional
from pydantic import BaseModel
from enum import Enum


class ContractCategory(Enum):
    ERC20 = "erc20"
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    UNI_SWAP_V2 = "UniSwapV2"


class ContractData(BaseModel):
    # contract address
    address: str
    code: str
    symbol: Optional[str]
    name: Optional[str]
    decimals: Optional[int]
    total_supply: Optional[float]
    token_category: str
