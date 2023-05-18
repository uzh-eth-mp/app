from hexbytes import HexBytes
from web3.contract import Contract
from web3.types import TxReceipt

from web3.logs import DISCARD
from app.model.contract import ContractCategory
from app.web3.transaction_events.decorator import _event_mapper
from app.web3.transaction_events.types import (
    FlashLoan,
    EventsGenerator,
)

# An example https://etherscan.io/tx/0x39fe19f9a43e8ea1a735097995fcb43a5b79eb42128415f1b6a391dedb590f72#eventlog
# The contract code https://github.com/aave/aave-protocol/blob/4b4545fb583fd4f400507b10f3c3114f45b8a037/contracts/lendingpool/LendingPool.sol#L843
@_event_mapper(ContractCategory.AAVE)
def _flash_loan(
    contract: Contract, receipt: TxReceipt, block_hash: HexBytes
) -> EventsGenerator:
    for eventLog in contract.events.FlashLoan().process_receipt(receipt, errors=DISCARD):
        if eventLog["event"] == "FlashLoan":
            yield FlashLoan(
                receiver=eventLog["args"]["_target"],
                reserve=eventLog["args"]["_reserve"],
                amount=eventLog["args"]["_amount"],
                totalFee=eventLog["args"]["_totalFee"],
                protocolFee=eventLog["args"]["_protocolFee"],
            ), eventLog
