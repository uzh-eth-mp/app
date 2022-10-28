from typing import Generator

from hexbytes import HexBytes
from web3.contract import Contract
from web3.types import TxReceipt

from app.model.contract import ContractCategory
from .decorator import _event_mapper
from app.web3.transaction_events.types import ContractEvent, PairCreatedEvent


@_event_mapper(ContractCategory.UNI_SWAP_V2_FACTORY)
def _pair_created(contract: Contract, receipt: TxReceipt, block_hash: HexBytes) -> Generator[ContractEvent, None, None]:
    # PairCreation -> https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Factory.sol#L13
    for eventLog in contract.events.PairCreated().processReceipt(receipt):
        if eventLog['event'] == 'PairCreated':
            token0 = eventLog['args']['token0']
            token1 = eventLog['args']['token1']
            pair = eventLog['args']['pair']
            yield PairCreatedEvent(
                contract_address=receipt["contractAddress"], pair_address=pair, token0=token0, token1=token1)