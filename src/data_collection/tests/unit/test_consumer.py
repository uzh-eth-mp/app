from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.model import DataCollectionMode
from app.model.contract import ContractCategory
from app.model.transaction import InternalTransactionData
from app.web3.transaction_events.types import (
    BurnFungibleEvent,
    BurnPairEvent,
    MintFungibleEvent,
    MintPairEvent,
    TransferFungibleEvent,
)


class TestHandleContractCreation:
    """Tests for _handle_contract_creation method in DataConsumer"""

    # TODO: Add tests for _handle_contract_creation method in DataConsumer
    pass


class TestHandleTransaction:
    """Tests for _handle_transaction method in DataConsumer"""

    async def test_tx_inserted_without_internal_txs(
        self,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
    ):
        """Test that insert to db is called once for a transaction without internal transactions"""
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        consumer.db_manager.insert_transaction = AsyncMock()
        consumer.node_connector.get_internal_transactions = AsyncMock()
        consumer.db_manager.insert_internal_transactions = AsyncMock()

        await consumer._handle_transaction(
            tx_data=transaction_data, tx_receipt_data=transaction_receipt_data
        )

        consumer.db_manager.insert_transaction.assert_awaited_once_with(
            **transaction_data.dict(),
            gas_used=transaction_receipt_data.gas_used,
            is_token_tx=True,
            transaction_fee=transaction_data.gas_price
            * transaction_receipt_data.gas_used,
        )
        consumer.db_manager.insert_internal_transactions.assert_not_awaited()

    async def test_tx_inserted_and_internal_txs_inserted(
        self,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
    ):
        """Test that insert to db is called once for a transaction and all internal transactions"""
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        consumer.db_manager.insert_transaction = AsyncMock()
        internal_tx_data = InternalTransactionData(
            **{
                "from": "0x0000000",
                "to": "0x0000000",
                "value": "0x1337",
                "gasUsed": "0x1337",
                "gas": "0x1337",
                "input": "0x0000000",
                "callType": "call",
            }
        )
        get_internal_txs_mock = AsyncMock()
        get_internal_txs_mock.return_value = [internal_tx_data, internal_tx_data]
        consumer.node_connector.get_internal_transactions = get_internal_txs_mock
        consumer.db_manager.insert_internal_transaction = AsyncMock()

        await consumer._handle_transaction(
            tx_data=transaction_data, tx_receipt_data=transaction_receipt_data
        )

        consumer.db_manager.insert_transaction.assert_awaited_once_with(
            **transaction_data.dict(),
            gas_used=transaction_receipt_data.gas_used,
            is_token_tx=True,
            transaction_fee=transaction_data.gas_price
            * transaction_receipt_data.gas_used,
        )
        consumer.node_connector.get_internal_transactions.assert_awaited_once_with(
            transaction_data.transaction_hash
        )
        assert consumer.db_manager.insert_internal_transaction.await_count == 2
        consumer.db_manager.insert_internal_transaction.assert_awaited_with(
            **internal_tx_data.dict(),
            transaction_hash=transaction_data.transaction_hash,
        )

    async def test_transaction_fee_correct(self):
        """Test that the transaction fee is calculated correctly in _handle_transaction"""
        # TODO: Implement
        pass


class TestHandleTransactionEvents:
    """Tests for _handle_transaction_events method in DataConsumer"""

    @patch("app.consumer.get_transaction_events")
    async def test_no_event_inserted(
        self,
        mock_get_transaction_events,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that no event is inserted if no event was found"""
        # Arrange
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "TransferFungibleEvent",
            "MintFungibleEvent",
            "BurnFungibleEvent",
        ]
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = []
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_not_awaited()
        consumer.db_manager.insert_contract_supply_change.assert_not_awaited()
        consumer.db_manager.insert_pair_liquidity_change.assert_not_awaited()

    @patch("app.consumer.get_transaction_events")
    @pytest.mark.parametrize(
        "event",
        [
            "transfer_fungible_event",
            "mint_fungible_event",
            "burn_fungible_event",
            "mint_pair_event",
            "burn_pair_event",
            "swap_pair_event",
        ],
    )
    async def test_no_event_inserted_if_not_in_config(
        self,
        mock_get_transaction_events,
        event,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
        request,
    ):
        """Test that no event is inserted if event found but is not in config"""
        # Arrange
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = []
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (
                request.getfixturevalue(event),
                dict(logIndex=1337),
            )
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_not_awaited()
        consumer.db_manager.insert_contract_supply_change.assert_not_awaited()
        consumer.db_manager.insert_pair_liquidity_change.assert_not_awaited()

    @patch("app.consumer.get_transaction_events")
    @pytest.mark.parametrize(
        "event,supply_change,liquidity_change",
        [
            ("transfer_fungible_event", None, None),
            ("mint_fungible_event", 1500, None),
            ("burn_fungible_event", -1500, None),
            ("mint_pair_event", None, (1500, 2500)),
            ("burn_pair_event", None, (-1500, -2500)),
            ("swap_pair_event", None, (200, 600)),
        ],
    )
    async def test_event_inserted_if_in_config(
        self,
        mock_get_transaction_events,
        event,
        supply_change,
        liquidity_change,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
        request,
    ):
        """Test every event is inserted if event found and is present in config"""
        # Arrange
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            request.getfixturevalue(event).__class__.__name__
        ]
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (
                request.getfixturevalue(event),
                dict(logIndex=1337),
            )
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = request.getfixturevalue(event).contract_address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_awaited_once_with(
            **transaction_logs_data.dict()
        )
        if supply_change:
            consumer.db_manager.insert_contract_supply_change.assert_awaited_once_with(
                address=request.getfixturevalue(event).contract_address,
                transaction_hash=transaction_data.transaction_hash,
                amount_changed=supply_change,
            )
        else:
            consumer.db_manager.insert_contract_supply_change.assert_not_awaited()
        if liquidity_change:
            consumer.db_manager.insert_pair_liquidity_change.assert_awaited_once_with(
                address=request.getfixturevalue(event).contract_address,
                amount0=liquidity_change[0],
                amount1=liquidity_change[1],
                transaction_hash=transaction_data.transaction_hash,
            )
        else:
            consumer.db_manager.insert_pair_liquidity_change.assert_not_awaited()

    @patch("app.consumer.get_transaction_events")
    async def test_transfer_fungible_to_dead_address_event_inserted(
        self,
        mock_get_transaction_events,
        dead_address,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that transfer to dead address is inserted as a log once and as a burn supply change"""
        # Arrange
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "TransferFungibleEvent",
            "BurnFungibleEvent",
        ]
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (
                BurnFungibleEvent(
                    contract_address=contract_config_usdt.address,
                    account="0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                    value=2000,
                ),
                dict(logIndex=1337),
            ),
            (
                TransferFungibleEvent(
                    contract_address=contract_config_usdt.address,
                    src="0xF00D",
                    dst=dead_address,
                    value=2000,
                ),
                dict(logIndex=1337),
            ),
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_awaited_once_with(
            **transaction_logs_data.dict()
        )
        consumer.db_manager.insert_contract_supply_change.assert_awaited_once_with(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            transaction_hash="0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
            amount_changed=-2000,
        )
        consumer.db_manager.insert_pair_liquidity_change.assert_not_awaited()

    @patch("app.consumer.get_transaction_events")
    async def test_transfer_fungible_to_dead_address_event_not_inserted_if_not_in_config(
        self,
        mock_get_transaction_events,
        dead_address,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that transfer to dead address is not inserted as a log nor as a supply change event if not in config"""
        # Arrange
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = []
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (
                TransferFungibleEvent(
                    contract_address=contract_config_usdt.address,
                    src="0xF00D",
                    dst=dead_address,
                    value=1500,
                ),
                dict(logIndex=1337),
            ),
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_not_awaited()
        consumer.db_manager.insert_contract_supply_change.assert_not_awaited()
        consumer.db_manager.insert_pair_liquidity_change.assert_not_awaited()

    @patch("app.consumer.get_transaction_events")
    async def test_transfer_fungible_from_dead_address_event_inserted(
        self,
        mock_get_transaction_events,
        dead_address,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that transfer from dead address is inserted as a log once and as a mint supply change"""
        # Arrange
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "TransferFungibleEvent",
            "MintFungibleEvent",
        ]
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (
                TransferFungibleEvent(
                    contract_address=contract_config_usdt.address,
                    src=dead_address,
                    dst="0xCAFE",
                    value=2500,
                ),
                dict(logIndex=1337),
            ),
            (
                MintFungibleEvent(
                    contract_address=contract_config_usdt.address,
                    account="0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                    value=1500,
                ),
                dict(logIndex=1337),
            ),
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_awaited_once_with(
            **transaction_logs_data.dict()
        )
        consumer.db_manager.insert_contract_supply_change.assert_awaited_once_with(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            transaction_hash="0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
            amount_changed=1500,
        )
        consumer.db_manager.insert_pair_liquidity_change.assert_not_awaited()

    @patch("app.consumer.get_transaction_events")
    async def test_transfer_fungible_from_dead_address_event_not_inserted_if_not_in_config(
        self,
        mock_get_transaction_events,
        dead_address,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that transfer from dead address is not inserted as a log nor as a supply change event if not in config"""
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = []
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (
                TransferFungibleEvent(
                    contract_address=contract_config_usdt.address,
                    src=dead_address,
                    dst="0xCAFE",
                    value=1500,
                ),
                dict(logIndex=1337),
            ),
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_not_awaited()
        consumer.db_manager.insert_contract_supply_change.assert_not_awaited()
        consumer.db_manager.insert_pair_liquidity_change.assert_not_awaited()

    @patch("app.consumer.get_transaction_events")
    async def test_mint_pair_event_from_dead_address(
        self,
        mock_get_transaction_events,
        dead_address,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that mint pair event from dead address is inserted as log and mint event"""
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = ["MintPairEvent"]
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (
                MintPairEvent(
                    contract_address=contract_config_usdt.address,
                    sender=dead_address,
                    amount0=1500,
                    amount1=2500,
                ),
                dict(logIndex=1337),
            )
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_awaited_once_with(
            **transaction_logs_data.dict()
        )
        consumer.db_manager.insert_contract_supply_change.assert_not_awaited()
        consumer.db_manager.insert_pair_liquidity_change.assert_awaited_once_with(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            amount0=1500,
            amount1=2500,
            transaction_hash="0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
        )

    @patch("app.consumer.get_transaction_events")
    async def test_burn_pair_event_from_dead_address_inserted(
        self,
        mock_get_transaction_events,
        dead_address,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that burn pair event to dead address is inserted as log and burn event"""
        # Arrange
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = ["BurnPairEvent"]
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (
                BurnPairEvent(
                    contract_address=contract_config_usdt.address,
                    src="0xCAFE",
                    dst=dead_address,
                    amount0=1500,
                    amount1=2500,
                ),
                dict(logIndex=1337),
            )
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_awaited_once_with(
            **transaction_logs_data.dict()
        )
        consumer.db_manager.insert_contract_supply_change.assert_not_awaited()
        consumer.db_manager.insert_pair_liquidity_change.assert_awaited_once_with(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            amount0=-1500,
            amount1=-2500,
            transaction_hash="0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
        )

    @patch("app.consumer.get_transaction_events")
    async def test_transfer_non_fungible_inserts_nft_transfer(
        self,
        mock_get_transaction_events,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        transfer_non_fungible_event,
        contract_config_bayc,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test TransferNonFungibleEvent is inserted as NFT transfer"""
        # Arrange
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_bayc])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = ["TransferNonFungibleEvent"]
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (
                transfer_non_fungible_event,
                dict(logIndex=1337),
            ),
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_bayc.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()
        consumer.db_manager.insert_nft_transfer = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_awaited_once_with(
            **transaction_logs_data.dict()
        )
        consumer.db_manager.insert_contract_supply_change.assert_not_awaited()
        consumer.db_manager.insert_pair_liquidity_change.assert_not_awaited()
        consumer.db_manager.insert_nft_transfer.assert_awaited_once_with(
            address="0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
            from_address="0xF00D",
            to_address="0xCAFE",
            token_id=1337,
            transaction_hash=transaction_data.transaction_hash,
        )

    @patch("app.consumer.get_transaction_events")
    async def test_mint_burn_fungible_combination(
        self,
        mock_get_transaction_events,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        burn_fungible_event,
        mint_fungible_event,
        contract_config_usdt,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that multiple mint/burn fungible events together are handled correctly"""
        # Arrange
        consumer = consumer_factory(
            config_factory([data_collection_config_factory([contract_config_usdt])]),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "MintFungibleEvent",
            "BurnFungibleEvent",
        ]
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (burn_fungible_event, dict(logIndex=1337)),
            (burn_fungible_event, dict(logIndex=1338)),
            (mint_fungible_event, dict(logIndex=1339)),
            (mint_fungible_event, dict(logIndex=1340)),
            (mint_fungible_event, dict(logIndex=1341)),
        ]
        logs = [transaction_logs_data] * 5
        for i, log in enumerate(logs):
            log.log_index = 1337 + i
        transaction_receipt_data.logs = logs
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_awaited_with(
            **logs[4].dict()
        )
        assert consumer.db_manager.insert_transaction_logs.await_count == 5
        consumer.db_manager.insert_contract_supply_change.assert_awaited_once_with(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            transaction_hash="0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
            amount_changed=1500,
        )
        consumer.db_manager.insert_pair_liquidity_change.assert_not_awaited()

    @patch("app.consumer.get_transaction_events")
    async def test_mint_burn_swap_pair_combination(
        self,
        mock_get_transaction_events,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        burn_pair_event,
        mint_pair_event,
        swap_pair_event,
        contract_config_pair_usdc_weth,
        contract_abi,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that multiple mint/burn/swap pair events together are handled correctly"""
        # Arrange
        consumer = consumer_factory(
            config_factory(
                [data_collection_config_factory([contract_config_pair_usdc_weth])]
            ),
            contract_abi,
        )
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "MintPairEvent",
            "BurnPairEvent",
            "SwapPairEvent",
        ]
        consumer.contract_parser.get_contract_events = get_contract_events_mock
        mock_get_transaction_events.return_value = [
            (burn_pair_event, dict(logIndex=1337)),
            (mint_pair_event, dict(logIndex=1338)),
            (burn_pair_event, dict(logIndex=1339)),
            (mint_pair_event, dict(logIndex=1340)),
            (swap_pair_event, dict(logIndex=1341)),
            (swap_pair_event, dict(logIndex=1342)),
            (mint_pair_event, dict(logIndex=1343)),
        ]
        logs = [transaction_logs_data] * 7
        for i, log in enumerate(logs):
            log.log_index = 1337 + i
        transaction_receipt_data.logs = logs
        contract_mock = Mock()
        contract_mock.address = contract_config_pair_usdc_weth.address
        consumer.db_manager.insert_transaction_logs = AsyncMock()
        consumer.db_manager.insert_contract_supply_change = AsyncMock()
        consumer.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        await consumer._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash=Mock(),
        )

        # Assert
        consumer.db_manager.insert_transaction_logs.assert_awaited_with(
            **logs[6].dict()
        )
        assert consumer.db_manager.insert_transaction_logs.await_count == 7
        consumer.db_manager.insert_contract_supply_change.assert_not_awaited()
        consumer.db_manager.insert_pair_liquidity_change.assert_awaited_with(
            address=contract_config_pair_usdc_weth.address,
            amount0=1900,
            amount1=3700,
            transaction_hash=transaction_data.transaction_hash,
        )


class TestOnKafkaEvent:
    """Tests for methods related to direct kafka event handling in DataConsumer"""

    @pytest.mark.parametrize(
        "mode", [DataCollectionMode.FULL, DataCollectionMode.PARTIAL]
    )
    async def test_on_kafka_event(
        self,
        mode,
        consumer_factory,
        config_factory,
        data_collection_config_factory,
        contract_config_usdt,
        contract_abi,
    ):
        """Test that a regular event (transaction) is handled for two modes: full and partial"""
        # Arrange
        data_collection_config = data_collection_config_factory([contract_config_usdt])
        data_collection_config.mode = mode
        consumer = consumer_factory(
            config_factory([data_collection_config]),
            contract_abi,
        )
        consumer.node_connector.get_transaction_data = AsyncMock()
        consumer.node_connector.get_transaction_data.return_value = (None, None)
        consumer.node_connector.get_transaction_receipt_data = AsyncMock()
        consumer.node_connector.get_transaction_receipt_data.return_value = (None, None)
        consumer._consume_full = AsyncMock()
        consumer._consume_partial = AsyncMock()
        kafka_event = Mock()
        kafka_event.value = f"{mode.value}:0x1234".encode()

        # Act
        await consumer._on_kafka_event(event=kafka_event)

        # Assert
        consumer.node_connector.get_transaction_data.assert_awaited_once()
        consumer.node_connector.get_transaction_receipt_data.assert_awaited_once()
        if mode == DataCollectionMode.FULL:
            consumer._consume_full.assert_awaited_once()
            consumer._consume_partial.assert_not_awaited()
        elif mode == DataCollectionMode.PARTIAL:
            consumer._consume_full.assert_not_awaited()
            consumer._consume_partial.assert_awaited_once()

        assert consumer._n_consumed_txs == 1

    async def test_consume_full_flow(
        self,
        default_consumer,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test _consume_full flow"""
        default_consumer._handle_transaction = AsyncMock()
        default_consumer.db_manager.insert_transaction_logs = AsyncMock()
        transaction_receipt_data.logs = [transaction_logs_data]

        await default_consumer._consume_full(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
        )

        default_consumer._handle_transaction.assert_awaited_once_with(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
        )
        default_consumer.db_manager.insert_transaction_logs.assert_awaited_once_with(
            **transaction_logs_data.dict()
        )
        assert default_consumer._n_processed_txs == 1

    async def test_consume_partial_unknown_contract_flow(
        self, default_consumer, transaction_data, transaction_receipt_data
    ):
        """Test _consume_partial flow if an unknown contract is encountered"""
        transaction_data.to_address = "0x1234"
        transaction_receipt_data.contract_address = "0x1234"
        default_consumer._handle_contract_creation = AsyncMock()
        default_consumer._handle_transaction = AsyncMock()
        default_consumer._handle_transaction_events = AsyncMock()
        w3_tx_data = MagicMock()
        w3_block_kv = {"blockHash": "0x0000"}
        w3_tx_data.__get__item.side_effect = w3_block_kv.__getitem__
        default_consumer.contract_parser.get_contract_category.return_value = None

        await default_consumer._consume_partial(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            w3_tx_data=w3_tx_data,
            w3_tx_receipt=Mock(),
        )

        assert default_consumer._n_processed_txs == 0
        default_consumer._handle_contract_creation.assert_not_awaited()
        default_consumer._handle_transaction.assert_not_awaited()
        default_consumer._handle_transaction_events.assert_not_awaited()

    async def test_consume_partial_known_contract_flow(
        self,
        default_consumer,
        transaction_data,
        transaction_receipt_data,
        contract_config_usdt,
    ):
        """Test _consume_partial flow if a known contract is encountered"""
        transaction_data.to_address = contract_config_usdt.address
        transaction_receipt_data.contract_address = contract_config_usdt.address
        default_consumer._handle_contract_creation = AsyncMock()
        default_consumer._handle_transaction = AsyncMock()
        default_consumer._handle_transaction_events = AsyncMock()
        default_consumer.contract_parser.get_contract_category.return_value = (
            ContractCategory(contract_config_usdt.category)
        )
        contract_mock = Mock()
        default_consumer.contract_parser.get_contract.return_value = contract_mock
        w3_tx_data = MagicMock()
        w3_tx_data.__getitem__.side_effect = dict(blockHash="0x0000").__getitem__
        w3_tx_receipt = Mock()

        await default_consumer._consume_partial(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            w3_tx_data=w3_tx_data,
            w3_tx_receipt=w3_tx_receipt,
        )

        assert default_consumer._n_processed_txs == 1
        default_consumer._handle_contract_creation.assert_not_awaited()
        default_consumer._handle_transaction.assert_awaited_once_with(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
        )
        default_consumer._handle_transaction_events.assert_awaited_once_with(
            contract=contract_mock,
            category=ContractCategory.ERC20,
            tx_data=transaction_data,
            tx_receipt=w3_tx_receipt,
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash="0x0000",
        )

    async def test_consume_partial_contract_creation_flow(
        self,
        default_consumer,
        transaction_data,
        transaction_receipt_data,
        contract_config_usdt,
    ):
        """Test _consume_partial flow if a contract is being created within this transaction"""
        transaction_data.to_address = None
        transaction_receipt_data.contract_address = contract_config_usdt.address
        default_consumer._handle_contract_creation = AsyncMock()
        default_consumer._handle_transaction = AsyncMock()
        default_consumer._handle_transaction_events = AsyncMock()
        default_consumer.contract_parser.get_contract_category.return_value = (
            ContractCategory(contract_config_usdt.category)
        )
        contract_mock = Mock()
        default_consumer.contract_parser.get_contract.return_value = contract_mock
        w3_tx_data = MagicMock()
        w3_tx_data.__getitem__.side_effect = dict(blockHash="0x0000").__getitem__
        w3_tx_receipt = Mock()

        await default_consumer._consume_partial(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            w3_tx_data=w3_tx_data,
            w3_tx_receipt=w3_tx_receipt,
        )

        assert default_consumer._n_processed_txs == 1
        default_consumer._handle_contract_creation.assert_awaited_once_with(
            contract=contract_mock,
            tx_data=transaction_data,
            category=ContractCategory.ERC20,
        )
        default_consumer._handle_transaction.assert_awaited_once_with(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
        )
        default_consumer._handle_transaction_events.assert_awaited_once_with(
            contract=contract_mock,
            category=ContractCategory.ERC20,
            tx_data=transaction_data,
            tx_receipt=w3_tx_receipt,
            tx_receipt_data=transaction_receipt_data,
            w3_block_hash="0x0000",
        )
