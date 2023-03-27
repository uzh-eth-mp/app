from hexbytes import HexBytes
from web3.contract import Contract
from web3.types import TxReceipt
from app.model.contract import ContractCategory
from . import erc20, erc721, uniswap_pair, uniswapv2_factory, decorator
from typing import (
    Generator,
    Type,
    Union,
)
from .types import ContractEvent


def get_transaction_events(
    contract_category: ContractCategory,
    contract: Union[Type[Contract], Contract],
    receipt: TxReceipt,
    block_hash: HexBytes,
) -> Generator[ContractEvent, None, None]:
    """
    It returns all the contract events found in the given contract with the given receipt.
    """
    if not isinstance(contract, Contract):
        return None
    for mapper in decorator.__event_mappers[contract_category]:
        yield from mapper(contract, receipt, block_hash)
