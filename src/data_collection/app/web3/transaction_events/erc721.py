from typing import Generator

from hexbytes import HexBytes
from web3.contract import Contract
from web3.types import TxReceipt

from app.model.contract import ContractCategory
from .decorator import _event_mapper
from app.web3.transaction_events.types import (
    BurnNonFungibleEvent,
    MintNonFungibleEvent,
    TransferNonFungibleEvent,
    ContractEvent,
)


@_event_mapper(ContractCategory.ERC721)
def _transaction(
    contract: Contract, receipt: TxReceipt, block_hash: HexBytes
) -> Generator[ContractEvent, None, None]:
    burn_addresses = {
        "0x0000000000000000000000000000000000000000",
        "0x000000000000000000000000000000000000dead",
    }

    for eventLog in contract.events.Transfer().processReceipt(receipt):
        if eventLog["event"] == "Transfer":
            src = eventLog["args"]["from"]
            dst = eventLog["args"]["to"]
            token_id = eventLog["args"]["tokenId"]
            if dst in burn_addresses and src in burn_addresses:
                pass
            if dst in burn_addresses:
                yield BurnNonFungibleEvent(
                    contract_address=receipt["contractAddress"],
                    account=src,
                    tokenId=token_id,
                )
            elif src in burn_addresses:
                yield MintNonFungibleEvent(
                    contract_address=receipt["contractAddress"],
                    account=dst,
                    tokenId=token_id,
                )
            else:
                yield TransferNonFungibleEvent(
                    contract_address=receipt["contractAddress"],
                    src=src,
                    dst=dst,
                    tokenId=token_id,
                )
