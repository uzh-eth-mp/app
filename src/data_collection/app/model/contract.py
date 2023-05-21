from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ContractCategory(Enum):
    UNKNOWN = "unknown"
    ERC20 = "erc20"
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    UNI_SWAP_V2_FACTORY = "UniSwapV2Factory"
    UNI_SWAP_V2_PAIR = "UniSwapV2Pair"

    @property
    def is_erc(self):
        """Return True if contract category is one of the ERC categories"""
        return self.value in [self.ERC20, self.ERC721, self.ERC1155]

    @property
    def is_uniswap_pair(self):
        """Return True if contract category is UniswapPair"""
        return self.value == self.UNI_SWAP_V2_PAIR


class TokenContractData(BaseModel):
    """Wrapper for web3 contract data that gets inserted into the db"""

    # contract address
    address: str
    symbol: Optional[str]
    name: Optional[str]
    decimals: Optional[int]
    total_supply: Optional[float]
    token_category: str


class PairContractData(BaseModel):
    """Wrapper for web3 pair contract data that gets inserted into the db"""

    address: str
    """The contract address (used as PK)"""
    token0: str
    """Address of token0"""
    token1: str
    """Address of token1"""
    reserve0: int
    reserve1: int
    factory: str
    """Address of the factory that created this pair contract"""
