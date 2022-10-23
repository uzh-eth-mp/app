from pydantic import BaseModel


class ContractEvent(BaseModel):
    """
    Contract events are the emitted events by the contract included in the transaction receipt (output of the
    interaction with a smart contract).
    """
    contract_address: str


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
    """
    account: str
    tokenId: str


class TransferNonFungibleEvent(ContractEvent):
    """
    This represents transfer event of NFTs between two addresses.
    """
    src: str
    dst: str
    tokenId: str
