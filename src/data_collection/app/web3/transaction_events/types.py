from typing import Generator, List, Optional, Tuple

from pydantic import BaseModel
from web3.types import EventData


class ContractEvent(BaseModel):
    """
    Contract events are the emitted events by the contract included in the transaction receipt (output of the
    interaction with a smart contract).
    """

    contract_address: Optional[str]
    name: str

    def should_process_event(self, event_names: List[str]):
        """Whether this event should be processed

        Returns:
            (bool): `True` if name is part of the event names
        """
        return self.name in event_names


class MintFungibleEvent(ContractEvent):
    """
    This represents mint event.
    """

    account: str
    value: int
    name = "Mint"


class BurnFungibleEvent(ContractEvent):
    """
    This represents burn event.
    """

    account: str
    value: int
    name = "Burn"


class TransferFungibleEvent(ContractEvent):
    """
    This represents transfer event between two addreses.
    """

    src: str
    dst: str
    value: int
    name = "Transfer"


class PairCreatedEvent(ContractEvent):
    """
    This represents the creation a contract for trading the token pair.
    """

    pair_address: str
    token0: str
    token1: str
    name = "PairCreated"


# https://ethereum.org/en/developers/tutorials/uniswap-v2-annotated-code/#pair-events
class MintPairEvent(ContractEvent):
    sender: str
    amount0: int
    amount1: int
    name = "Mint"


class BurnPairEvent(ContractEvent):
    src: str
    dst: str
    amount0: int
    amount1: int
    name = "Burn"


class SwapPairEvent(ContractEvent):
    src: str
    dst: str
    in0: int
    in1: int
    out0: int
    out1: int
    name = "Swap"


class MintNonFungibleEvent(ContractEvent):
    """
    This represents mint event.
    """

    account: str
    tokenId: str
    name = "Mint"


class BurnNonFungibleEvent(ContractEvent):
    """
    This represents burn event.
    https://github.com/ethereum/solidity-underhanded-contest/blob/cc7834ec9e8c804fe9e02735f77ddb22e69f5891/2022/
    submissions_2022/submission11_DanielVonFange/lib/openzeppelin-contracts/contracts/token/ERC721/ERC721.sol#L302


    """

    account: str
    tokenId: int
    name = "Burn"


class TransferNonFungibleEvent(ContractEvent):
    """
    This represents transfer event of NFTs between two addresses.
    """

    src: str
    dst: str
    tokenId: int
    name = "Transfer"


EventsGenerator = Generator[Tuple[ContractEvent, EventData], None, None]
