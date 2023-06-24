from typing import Generator, List, Optional, Tuple

from pydantic import BaseModel
from web3.types import EventData


class ContractEvent(BaseModel):
    """
    Contract events are the emitted events by the contract included in the transaction receipt (output of the
    interaction with a smart contract).
    """

    address: Optional[bytes]
    log_index: int


class MintFungibleEvent(ContractEvent):
    """
    This represents mint event.
    """

    value: int


class BurnFungibleEvent(ContractEvent):
    """
    This represents burn event.
    """

    value: int


class TransferFungibleEvent(ContractEvent):
    """
    This represents transfer event between two addreses.
    """

    src: bytes
    dst: bytes
    value: int


class PairCreatedEvent(ContractEvent):
    """
    This represents the creation a contract for trading the token pair.
    """

    pair_address: bytes
    token0: bytes
    token1: bytes


# https://ethereum.org/en/developers/tutorials/uniswap-v2-annotated-code/#pair-events
class MintPairEvent(ContractEvent):
    sender: bytes
    amount0: int
    amount1: int


class BurnPairEvent(ContractEvent):
    src: bytes
    dst: bytes
    amount0: int
    amount1: int


class SwapPairEvent(ContractEvent):
    src: bytes
    dst: bytes
    in0: int
    in1: int
    out0: int
    out1: int


class MintNonFungibleEvent(ContractEvent):
    """
    This represents mint event.
    """

    tokenId: bytes


class BurnNonFungibleEvent(ContractEvent):
    """
    This represents burn event.
    https://github.com/ethereum/solidity-underhanded-contest/blob/cc7834ec9e8c804fe9e02735f77ddb22e69f5891/2022/
    submissions_2022/submission11_DanielVonFange/lib/openzeppelin-contracts/contracts/token/ERC721/ERC721.sol#L302


    """

    tokenId: int


class TransferNonFungibleEvent(ContractEvent):
    """
    This represents transfer event of NFTs between two addresses.
    """

    src: bytes
    dst: bytes
    tokenId: int


EventsGenerator = Generator[ContractEvent, None, None]
