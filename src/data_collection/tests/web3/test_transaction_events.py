import unittest
from unittest.mock import MagicMock

from hexbytes import HexBytes
from web3.types import TxReceipt, EventData

from app.web3 import transaction_events as te
from app.model.contract import ContractCategory
from web3.contract import Contract
from web3.contract.contract import (
    ContractEvent,
    ContractEvents,
    ContractFunction,
    ContractFunctions,
)

from app.web3.transaction_events.types import (
    MintFungibleEvent,
    MintNonFungibleEvent,
    BurnNonFungibleEvent,
    TransferNonFungibleEvent,
    BurnFungibleEvent,
    TransferFungibleEvent,
    PairCreatedEvent,
    MintPairEvent,
    BurnPairEvent,
    SwapPairEvent,
)


class CommonTest(unittest.TestCase):
    def test_unknown_category_no_events(self):
        contract = MagicMock(spec=Contract)
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.UNKNOWN, contract, receipt, block_hash
        )
        events = list(events)

        contract.events.assert_not_called()
        self.assertEqual(len(events), 0)


class ERC20Tests(unittest.TestCase):
    def test_erc20_mint_transfer0x000(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Transfer",
                    args={
                        "from": "0x0000000000000000000000000000000000000000",
                        "to": "0x000000000000000000000000000000000000BABA",
                        "value": 42,
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(return_value=[])
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(return_value=[])
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.ERC20, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    MintFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        account="0x000000000000000000000000000000000000BABA",
                        value=42,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x0000000000000000000000000000000000000000",
                            "to": "0x000000000000000000000000000000000000BABA",
                            "value": 42,
                        },
                        logIndex=1337,
                    ),
                ),
                (
                    TransferFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x0000000000000000000000000000000000000000",
                        dst="0x000000000000000000000000000000000000BABA",
                        value=42,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x0000000000000000000000000000000000000000",
                            "to": "0x000000000000000000000000000000000000BABA",
                            "value": 42,
                        },
                        logIndex=1337,
                    ),
                ),
            ],
            events,
        )

    def test_erc20_mint_transfer0xdead(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Transfer",
                    args={
                        "from": "0x000000000000000000000000000000000000dead",
                        "to": "0x000000000000000000000000000000000000BABA",
                        "value": 42,
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(return_value=[])
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(return_value=[])
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.ERC20, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    MintFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        account="0x000000000000000000000000000000000000BABA",
                        value=42,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000dead",
                            "to": "0x000000000000000000000000000000000000BABA",
                            "value": 42,
                        },
                        logIndex=1337,
                    ),
                ),
                (
                    TransferFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x000000000000000000000000000000000000dead",
                        dst="0x000000000000000000000000000000000000BABA",
                        value=42,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000dead",
                            "to": "0x000000000000000000000000000000000000BABA",
                            "value": 42,
                        },
                        logIndex=1337,
                    ),
                ),
            ],
            events,
        )

    def test_erc20_usdt_mint_issue(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(return_value=[])
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(
            return_value=[EventData(event="Issue", args={"amount": 42}, logIndex=1337)]
        )
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(return_value=[])
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)
        contract.functions = MagicMock(spec=ContractFunctions)
        getOwner_function = MagicMock(spec=ContractFunction)
        getOwner_function.call = MagicMock(
            return_value="0x000000000000000000000000000000000000BABA"
        )
        contract.functions.getOwner = MagicMock(return_value=getOwner_function)

        events = te.get_transaction_events(
            ContractCategory.ERC20, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    MintFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        account="0x000000000000000000000000000000000000BABA",
                        value=42,
                    ),
                    EventData(event="Issue", args={"amount": 42}, logIndex=1337),
                )
            ],
            events,
        )

    def test_erc20_burn_transfer0x000(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Transfer",
                    args={
                        "from": "0x000000000000000000000000000000000000BABA",
                        "to": "0x0000000000000000000000000000000000000000",
                        "value": 42,
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(return_value=[])
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(return_value=[])
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.ERC20, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    BurnFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        account="0x000000000000000000000000000000000000BABA",
                        value=42,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "value": 42,
                            "from": "0x000000000000000000000000000000000000BABA",
                            "to": "0x0000000000000000000000000000000000000000",
                        },
                        logIndex=1337,
                    ),
                ),
                (
                    TransferFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x000000000000000000000000000000000000BABA",
                        dst="0x0000000000000000000000000000000000000000",
                        value=42,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "value": 42,
                            "from": "0x000000000000000000000000000000000000BABA",
                            "to": "0x0000000000000000000000000000000000000000",
                        },
                        logIndex=1337,
                    ),
                ),
            ],
            events,
        )

    def test_erc20_burn_transfer0xdead(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Transfer",
                    args={
                        "from": "0x000000000000000000000000000000000000BABA",
                        "to": "0x000000000000000000000000000000000000dead",
                        "value": 42,
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(return_value=[])
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(return_value=[])
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.ERC20, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    BurnFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        account="0x000000000000000000000000000000000000BABA",
                        value=42,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000BABA",
                            "to": "0x000000000000000000000000000000000000dead",
                            "value": 42,
                        },
                        logIndex=1337,
                    ),
                ),
                (
                    TransferFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x000000000000000000000000000000000000BABA",
                        dst="0x000000000000000000000000000000000000dead",
                        value=42,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000BABA",
                            "to": "0x000000000000000000000000000000000000dead",
                            "value": 42,
                        },
                        logIndex=1337,
                    ),
                ),
            ],
            events,
        )

    def test_erc20_burn_redeem(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(return_value=[])
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(return_value=[])
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(
            return_value=[EventData(event="Redeem", args={"amount": 42}, logIndex=1337)]
        )
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)
        contract.functions = MagicMock(spec=ContractFunctions)
        getOwner_function = MagicMock(spec=ContractFunction)
        getOwner_function.call = MagicMock(
            return_value="0x000000000000000000000000000000000000BABA"
        )
        contract.functions.getOwner = MagicMock(return_value=getOwner_function)

        events = te.get_transaction_events(
            ContractCategory.ERC20, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    BurnFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        account="0x000000000000000000000000000000000000BABA",
                        value=42,
                    ),
                    EventData(event="Redeem", args={"amount": 42}, logIndex=1337),
                )
            ],
            events,
        )

    def test_erc20_transfer(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Transfer",
                    args={
                        "from": "0x000000000000000000000000000000000000ABAB",
                        "to": "0x000000000000000000000000000000000000BABA",
                        "value": 42,
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(return_value=[])
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(return_value=[])
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.ERC20, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    TransferFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x000000000000000000000000000000000000ABAB",
                        dst="0x000000000000000000000000000000000000BABA",
                        value=42,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000ABAB",
                            "to": "0x000000000000000000000000000000000000BABA",
                            "value": 42,
                        },
                        logIndex=1337,
                    ),
                )
            ],
            events,
        )


class ERC721Tests(unittest.TestCase):
    def test_erc721_mint_transfer0x000(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Transfer",
                    args={
                        "from": "0x0000000000000000000000000000000000000000",
                        "to": "0x000000000000000000000000000000000000BABA",
                        "tokenId": 4,
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.ERC721, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    MintNonFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        account="0x000000000000000000000000000000000000BABA",
                        tokenId=4,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x0000000000000000000000000000000000000000",
                            "to": "0x000000000000000000000000000000000000BABA",
                            "tokenId": 4,
                        },
                        logIndex=1337,
                    ),
                ),
                (
                    TransferNonFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x0000000000000000000000000000000000000000",
                        dst="0x000000000000000000000000000000000000BABA",
                        tokenId=4,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x0000000000000000000000000000000000000000",
                            "to": "0x000000000000000000000000000000000000BABA",
                            "tokenId": 4,
                        },
                        logIndex=1337,
                    ),
                ),
            ],
            events,
        )

    def test_erc721_mint_transfer0xdead(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Transfer",
                    args={
                        "from": "0x000000000000000000000000000000000000dead",
                        "to": "0x000000000000000000000000000000000000BABA",
                        "tokenId": 4,
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(return_value=[])
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(return_value=[])
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.ERC721, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    MintNonFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        account="0x000000000000000000000000000000000000BABA",
                        tokenId=4,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000dead",
                            "to": "0x000000000000000000000000000000000000BABA",
                            "tokenId": 4,
                        },
                        logIndex=1337,
                    ),
                ),
                (
                    TransferNonFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x000000000000000000000000000000000000dead",
                        dst="0x000000000000000000000000000000000000BABA",
                        tokenId=4,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000dead",
                            "to": "0x000000000000000000000000000000000000BABA",
                            "tokenId": 4,
                        },
                        logIndex=1337,
                    ),
                ),
            ],
            events,
        )

    def test_erc721_burn_transfer0x00(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Transfer",
                    args={
                        "from": "0x000000000000000000000000000000000000BABA",
                        "to": "0x0000000000000000000000000000000000000000",
                        "tokenId": 4,
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(return_value=[])
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(return_value=[])
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.ERC721, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    BurnNonFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        account="0x000000000000000000000000000000000000BABA",
                        tokenId=4,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000BABA",
                            "to": "0x0000000000000000000000000000000000000000",
                            "tokenId": 4,
                        },
                        logIndex=1337,
                    ),
                ),
                (
                    TransferNonFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x000000000000000000000000000000000000BABA",
                        dst="0x0000000000000000000000000000000000000000",
                        tokenId=4,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000BABA",
                            "to": "0x0000000000000000000000000000000000000000",
                            "tokenId": 4,
                        },
                        logIndex=1337,
                    ),
                ),
            ],
            events,
        )

    def test_erc721_burn_transfer0xdead(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Transfer",
                    args={
                        "from": "0x000000000000000000000000000000000000BABA",
                        "to": "0x000000000000000000000000000000000000dead",
                        "tokenId": 4,
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(return_value=[])
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(return_value=[])
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.ERC721, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    BurnNonFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        account="0x000000000000000000000000000000000000BABA",
                        tokenId=4,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000BABA",
                            "to": "0x000000000000000000000000000000000000dead",
                            "tokenId": 4,
                        },
                        logIndex=1337,
                    ),
                ),
                (
                    TransferNonFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x000000000000000000000000000000000000BABA",
                        dst="0x000000000000000000000000000000000000dead",
                        tokenId=4,
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000BABA",
                            "to": "0x000000000000000000000000000000000000dead",
                            "tokenId": 4,
                        },
                        logIndex=1337,
                    ),
                ),
            ],
            events,
        )

    def test_erc721_transfer(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        transfer_event = MagicMock(spec=ContractEvent)
        transfer_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Transfer",
                    args={
                        "from": "0x000000000000000000000000000000000000BABA",
                        "to": "0x000000000000000000000000000000000000ABAB",
                        "tokenId": "5",
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Transfer = MagicMock(return_value=transfer_event)
        issue_event = MagicMock(spec=ContractEvent)
        issue_event.process_receipt = MagicMock(return_value=[])
        contract.events.Issue = MagicMock(return_value=issue_event)
        redeem_event = MagicMock(spec=ContractEvent)
        redeem_event.process_receipt = MagicMock(return_value=[])
        contract.events.Redeem = MagicMock(return_value=redeem_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.ERC721, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    TransferNonFungibleEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x000000000000000000000000000000000000BABA",
                        dst="0x000000000000000000000000000000000000ABAB",
                        tokenId="5",
                    ),
                    EventData(
                        event="Transfer",
                        args={
                            "from": "0x000000000000000000000000000000000000BABA",
                            "to": "0x000000000000000000000000000000000000ABAB",
                            "tokenId": "5",
                        },
                        logIndex=1337,
                    ),
                )
            ],
            events,
        )


class UniSwapV2Tests(unittest.TestCase):
    def test_uniSwapV2_newPair(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        pairCreated_event = MagicMock(spec=ContractEvent)
        pairCreated_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="PairCreated",
                    args={
                        "token0": "0x0000000000000000000000000000000000000001",
                        "token1": "0x0000000000000000000000000000000000000002",
                        "pair": "0x0000000000000000000000000000000000000003",
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.PairCreated = MagicMock(return_value=pairCreated_event)
        receipt = MagicMock(spec=TxReceipt)
        receipt.__getitem__ = (
            lambda _, x: "0x000000000000000000000000000000000000AAAA"
            if x == "contractAddress"
            else None
        )
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.UNI_SWAP_V2_FACTORY, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    PairCreatedEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        pair_address="0x0000000000000000000000000000000000000003",
                        token0="0x0000000000000000000000000000000000000001",
                        token1="0x0000000000000000000000000000000000000002",
                    ),
                    EventData(
                        event="PairCreated",
                        args={
                            "token0": "0x0000000000000000000000000000000000000001",
                            "token1": "0x0000000000000000000000000000000000000002",
                            "pair": "0x0000000000000000000000000000000000000003",
                        },
                        logIndex=1337,
                    ),
                )
            ],
            events,
        )

    def test_uniSwapV2Pair_mint(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        Mint_event = MagicMock(spec=ContractEvent)
        Mint_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Mint",
                    args={
                        "sender": "0x0000000000000000000000000000000000000001",
                        "amount0": 2,
                        "amount1": 3,
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Mint = MagicMock(return_value=Mint_event)
        Burn_event = MagicMock(spec=ContractEvent)
        Burn_event.process_receipt = MagicMock(return_value=[])
        contract.events.Burn = MagicMock(return_value=Burn_event)
        Swap_event = MagicMock(spec=ContractEvent)
        Swap_event.process_receipt = MagicMock(return_value=[])
        contract.events.Swap = MagicMock(return_value=Swap_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.UNI_SWAP_V2_PAIR, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    MintPairEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        sender="0x0000000000000000000000000000000000000001",
                        amount0=2,
                        amount1=3,
                    ),
                    EventData(
                        event="Mint",
                        args={
                            "sender": "0x0000000000000000000000000000000000000001",
                            "amount0": 2,
                            "amount1": 3,
                        },
                        logIndex=1337,
                    ),
                )
            ],
            events,
        )

    def test_uniSwapV2Pair_burn(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        Burn_event = MagicMock(spec=ContractEvent)
        Burn_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Burn",
                    args={
                        "sender": "0x0000000000000000000000000000000000000001",
                        "amount0": 2,
                        "amount1": 3,
                        "to": "0x0000000000000000000000000000000000000002",
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Burn = MagicMock(return_value=Burn_event)
        Mint_event = MagicMock(spec=ContractEvent)
        Mint_event.process_receipt = MagicMock(return_value=[])
        contract.events.Mint = MagicMock(return_value=Mint_event)
        Swap_event = MagicMock(spec=ContractEvent)
        Swap_event.process_receipt = MagicMock(return_value=[])
        contract.events.Swap = MagicMock(return_value=Swap_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.UNI_SWAP_V2_PAIR, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    BurnPairEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x0000000000000000000000000000000000000001",
                        dst="0x0000000000000000000000000000000000000002",
                        amount0=2,
                        amount1=3,
                    ),
                    EventData(
                        event="Burn",
                        args={
                            "sender": "0x0000000000000000000000000000000000000001",
                            "amount0": 2,
                            "amount1": 3,
                            "to": "0x0000000000000000000000000000000000000002",
                        },
                        logIndex=1337,
                    ),
                )
            ],
            events,
        )

    def test_uniSwapV2Pair_swap(self):
        contract = MagicMock(spec=Contract)
        contract.events = MagicMock(spec=ContractEvents)
        Burn_event = MagicMock(spec=ContractEvent)
        Burn_event.process_receipt = MagicMock(spec=ContractEvent)
        contract.events.Burn = MagicMock(return_value=Burn_event)
        Mint_event = MagicMock(spec=ContractEvent)
        Mint_event.process_receipt = MagicMock(return_value=[])
        contract.events.Mint = MagicMock(return_value=Mint_event)
        Swap_event = MagicMock(spec=ContractEvent)
        Swap_event.process_receipt = MagicMock(
            return_value=[
                EventData(
                    event="Swap",
                    args={
                        "sender": "0x0000000000000000000000000000000000000001",
                        "amount0In": 2,
                        "amount1In": 3,
                        "amount0Out": 4,
                        "amount1Out": 5,
                        "to": "0x0000000000000000000000000000000000000002",
                    },
                    logIndex=1337,
                )
            ]
        )
        contract.events.Swap = MagicMock(return_value=Swap_event)
        contract.address = "0x000000000000000000000000000000000000AAAA"
        receipt = MagicMock(spec=TxReceipt)
        block_hash = MagicMock(spec=HexBytes)

        events = te.get_transaction_events(
            ContractCategory.UNI_SWAP_V2_PAIR, contract, receipt, block_hash
        )
        events = list(events)

        self.assertEqual(
            [
                (
                    SwapPairEvent(
                        contract_address="0x000000000000000000000000000000000000AAAA",
                        src="0x0000000000000000000000000000000000000001",
                        dst="0x0000000000000000000000000000000000000002",
                        in0=2,
                        in1=3,
                        out0=4,
                        out1=5,
                    ),
                    EventData(
                        event="Swap",
                        args={
                            "sender": "0x0000000000000000000000000000000000000001",
                            "amount0In": 2,
                            "amount1In": 3,
                            "amount0Out": 4,
                            "amount1Out": 5,
                            "to": "0x0000000000000000000000000000000000000002",
                        },
                        logIndex=1337,
                    ),
                )
            ],
            events,
        )


if __name__ == "__main__":
    unittest.main()
