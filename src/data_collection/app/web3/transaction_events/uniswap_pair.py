from hexbytes import HexBytes
from web3.contract import Contract
from web3.types import TxReceipt
from app import init_logger

from app.model.contract import ContractCategory
from .decorator import _event_mapper
from typing import Generator

from app.web3.transaction_events.types import (
    MintPairEvent,
    BurnPairEvent,
    SwapPairEvent,
    ContractEvent,
)

log = init_logger(__name__)


@_event_mapper(ContractCategory.UNI_SWAP_V2_PAIR)
def _mint(
    contract: Contract, receipt: TxReceipt, block_hash: HexBytes
) -> Generator[ContractEvent, None, None]:
    for eventLog in contract.events.Mint().processReceipt(receipt):
        sender = eventLog["args"]["sender"]
        amount0 = eventLog["args"]["amount0"]
        amount1 = eventLog["args"]["amount1"]
        yield MintPairEvent(
            contract_address=receipt["contractAddress"],
            sender=sender,
            amount0=amount0,
            amount1=amount1,
        )


@_event_mapper(ContractCategory.UNI_SWAP_V2_PAIR)
def _burn(
    contract: Contract, receipt: TxReceipt, block_hash: HexBytes
) -> Generator[ContractEvent, None, None]:
    # https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol#L134
    # Burn of pairs in Uniswap -> taking back liquidity from the pool "to" their address or another one.
    for eventLog in contract.events.Burn().processReceipt(receipt):
        sender = eventLog["args"]["sender"]
        amount0 = eventLog["args"]["amount0"]
        amount1 = eventLog["args"]["amount1"]
        to = eventLog["args"]["to"]
        yield BurnPairEvent(
            contract_address=receipt["contractAddress"],
            src=sender,
            dst=to,
            amount0=amount0,
            amount1=amount1,
        )


@_event_mapper(ContractCategory.UNI_SWAP_V2_PAIR)
def _swap(
    contract: Contract, receipt: TxReceipt, block_hash: HexBytes
) -> Generator[ContractEvent, None, None]:
    # https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol#L51
    log.error("Extracting swaps!")
    for eventLog in contract.events.Swap().processReceipt(receipt):
        sender = eventLog["args"]["sender"]
        amount_0_in = eventLog["args"]["amount0In"]
        amount_1_in = eventLog["args"]["amount1In"]
        amount_0_out = eventLog["args"]["amount0Out"]
        amount_1_out = eventLog["args"]["amount1Out"]
        to = eventLog["args"]["to"]
        log.error("Swap found!")
        yield SwapPairEvent(
            contract_address=receipt["contractAddress"],
            src=sender,
            dst=to,
            in0=amount_0_in,
            in1=amount_1_in,
            out0=amount_0_out,
            out1=amount_1_out,
        )
