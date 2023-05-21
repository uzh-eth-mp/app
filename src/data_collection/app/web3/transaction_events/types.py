from typing import Generator, List, Optional, Tuple

from pydantic import BaseModel
from web3.types import EventData


class ContractEvent(BaseModel):
    """
    Contract events are the emitted events by the contract included in the transaction receipt (output of the
    interaction with a smart contract).
    """

    contract_address: Optional[str]


class MintFungibleEvent(ContractEvent):
    """
    This represents mint event.
    """

    account: str
    value: int


class BurnFungibleEvent(ContractEvent):
    """
    This represents burn event.
    """

    account: str
    value: int


class TransferFungibleEvent(ContractEvent):
    """
    This represents transfer event between two addreses.
    """

    src: str
    dst: str
    value: int


class PairCreatedEvent(ContractEvent):
    """
    This represents the creation a contract for trading the token pair.
    """

    pair_address: str
    token0: str
    token1: str


# https://ethereum.org/en/developers/tutorials/uniswap-v2-annotated-code/#pair-events
class MintPairEvent(ContractEvent):
    sender: str
    amount0: int
    amount1: int


class BurnPairEvent(ContractEvent):
    src: str
    dst: str
    amount0: int
    amount1: int


class SwapPairEvent(ContractEvent):
    src: str
    dst: str
    in0: int
    in1: int
    out0: int
    out1: int


class MintNonFungibleEvent(ContractEvent):
    """
    This represents mint event.
    """

    account: str
    tokenId: str


class BurnNonFungibleEvent(ContractEvent):
    """
    This represents burn event.
    https://github.com/ethereum/solidity-underhanded-contest/blob/cc7834ec9e8c804fe9e02735f77ddb22e69f5891/2022/
    submissions_2022/submission11_DanielVonFange/lib/openzeppelin-contracts/contracts/token/ERC721/ERC721.sol#L302


    """

    account: str
    tokenId: int


class TransferNonFungibleEvent(ContractEvent):
    """
    This represents transfer event of NFTs between two addresses.
    """

    src: str
    dst: str
    tokenId: int

class FlashLoan(ContractEvent):
    """
    This represents a flashloan.
    """
    receiver: str # The address of the contract receiving the funds.
    reserve: str # the address of the principal reserve
    amount: int # the amount requested for this flashloan
    totalFee: int # The total fees of this flashloan.
    protocolFee: int # The protocol fees of this flashloan.


EventsGenerator = Generator[Tuple[ContractEvent, EventData], None, None]
