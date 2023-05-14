import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.model.transaction import InternalTransactionData
from app.web3.transaction_events.types import (
    TransferFungibleEvent,
    BurnFungibleEvent,
    MintFungibleEvent,
    MintPairEvent,
    BurnPairEvent,
    SwapPairEvent,
    TransferNonFungibleEvent,
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
            * transaction_receipt_data.gas_used
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
            * transaction_receipt_data.gas_used
        )
        consumer.node_connector.get_internal_transactions.assert_awaited_once_with(
            transaction_data.transaction_hash
        )
        assert consumer.db_manager.insert_internal_transaction.await_count == 2
        consumer.db_manager.insert_internal_transaction.assert_awaited_with(
            **internal_tx_data.dict(),
            transaction_hash=transaction_data.transaction_hash
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


class TestOnKafkaEvent:
    """Tests for _on_kafka_event method in DataConsumer"""

    async def test_event_handled(self):
        """Test that a regular event (transaction) is handled"""
        # TODO: Implement
        pass

    async def test_event_not_handled_if_contract_is_not_in_config(self):
        """Test that an event is not handled if contract is not in config"""
        # TODO: Implement
        pass

    async def test_event_not_handled_if_event_is_not_in_config(self):
        """Test that an event is not handled if event is not in config"""
        # TODO: Implement
        pass

    async def test_handle_contract_creation_called_if_needed(self):
        """Test that handle_contract_creation is called if a new contract is created"""
        # TODO: Implement
        pass
