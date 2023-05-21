from hexbytes import HexBytes
from web3.contract import Contract

# Discarding errors on filtered events is expected
# https://github.com/oceanprotocol/ocean.py/issues/348#issuecomment-875128102
from web3.logs import DISCARD
from web3.types import TxReceipt

from app.model.contract import ContractCategory
from app.web3.transaction_events.decorator import _event_mapper
from app.web3.transaction_events.types import (
    BurnNonFungibleEvent,
    EventsGenerator,
    MintNonFungibleEvent,
    TransferNonFungibleEvent,
)


@_event_mapper(ContractCategory.ERC721)
def _transaction(
    contract: Contract, receipt: TxReceipt, block_hash: HexBytes
) -> EventsGenerator:
    burn_addresses = {
        "0x0000000000000000000000000000000000000000",
        "0x000000000000000000000000000000000000dead",
    }

    for eventLog in contract.events.Transfer().process_receipt(receipt, errors=DISCARD):
        if eventLog["event"] == "Transfer":
            src = eventLog["args"]["from"]
            dst = eventLog["args"]["to"]
            token_id = eventLog["args"]["tokenId"]
            if dst in burn_addresses and src in burn_addresses:
                pass
            if dst in burn_addresses:
                yield BurnNonFungibleEvent(
                    contract_address=contract.address,
                    account=src,
                    tokenId=token_id,
                ), eventLog
            elif src in burn_addresses:
                yield MintNonFungibleEvent(
                    contract_address=contract.address,
                    account=dst,
                    tokenId=token_id,
                ), eventLog

            yield TransferNonFungibleEvent(
                contract_address=contract.address,
                src=src,
                dst=dst,
                tokenId=token_id,
            ), eventLog
