from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.consumer.tx_processor import (
    FullTransactionProcessor,
    LogFilterTransactionProcessor,
    PartialTransactionProcessor,
)
from app.db.manager import DatabaseManager
from app.model.contract import ContractCategory
from app.model.transaction import InternalTransactionData
from app.web3.transaction_events.types import (
    BurnFungibleEvent,
    BurnPairEvent,
    MintFungibleEvent,
    MintPairEvent,
    TransferFungibleEvent,
)


class TestTransactionProcessor:
    """Tests for TransactionProcessor base class methods"""

    def test_handle_contract_creation(self):
        """Test that handle_contract_creation method is called"""
        # TODO: implement
        pass

    async def test_handle_transaction_without_internal_txs(
        self, transaction_data, transaction_receipt_data, transaction_processor
    ):
        """Test that in _handle_transaction insert to db is called once for a transaction without internal transactions"""
        # Arrange
        get_internal_transactions_mock = AsyncMock()
        get_internal_transactions_mock.return_value = []
        transaction_processor.node_connector.get_internal_transactions = AsyncMock()

        # Act
        await transaction_processor._handle_transaction(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            log_indices_to_save=set([]),
        )

        # Assert
        transaction_processor.db_manager.insert_transaction.assert_awaited_once_with(
            **transaction_data.dict(),
            gas_used=transaction_receipt_data.gas_used,
            is_token_tx=True,
            transaction_fee=transaction_data.gas_price
            * transaction_receipt_data.gas_used,
        )
        transaction_processor.db_manager.insert_internal_transaction.assert_not_awaited()
        transaction_processor.db_manager.insert_transaction_logs.assert_not_awaited()

    async def test_handle_transaction_with_internal_txs(
        self,
        transaction_processor,
        transaction_data,
        transaction_receipt_data,
    ):
        """Test that insert to db is called once for a transaction and all internal transactions"""
        # Arrange
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
        get_internal_transactions_mock = AsyncMock()
        get_internal_transactions_mock.return_value = [
            internal_tx_data,
            internal_tx_data,
        ]
        transaction_processor.node_connector.get_internal_transactions = (
            get_internal_transactions_mock
        )

        # Act
        await transaction_processor._handle_transaction(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            log_indices_to_save=set([]),
        )

        # Assert
        transaction_processor.db_manager.insert_transaction.assert_awaited_once_with(
            **transaction_data.dict(),
            gas_used=transaction_receipt_data.gas_used,
            is_token_tx=True,
            transaction_fee=transaction_data.gas_price
            * transaction_receipt_data.gas_used,
        )
        transaction_processor.node_connector.get_internal_transactions.assert_awaited_once_with(
            transaction_data.transaction_hash
        )
        assert (
            transaction_processor.db_manager.insert_internal_transaction.await_count
            == 2
        )
        transaction_processor.db_manager.insert_internal_transaction.assert_awaited_with(
            **internal_tx_data.dict(),
            transaction_hash=transaction_data.transaction_hash,
        )
        transaction_processor.db_manager.insert_transaction_logs.assert_not_awaited()

    async def test_handle_transaction_with_logs(
        self,
        transaction_processor,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that insert to db is called once for a transaction and all logs"""
        # Arrange
        transaction_receipt_data.logs = [transaction_logs_data, transaction_logs_data]
        transaction_receipt_data.logs[0].log_index = 230
        transaction_receipt_data.logs[1].log_index = 231
        transaction_processor.node_connector.get_internal_transactions = AsyncMock()

        # Act
        await transaction_processor._handle_transaction(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            log_indices_to_save=set([230, 231]),
        )

        # Assert
        transaction_processor.db_manager.insert_transaction.assert_awaited_once_with(
            **transaction_data.dict(),
            gas_used=transaction_receipt_data.gas_used,
            is_token_tx=True,
            transaction_fee=transaction_data.gas_price
            * transaction_receipt_data.gas_used,
        )
        transaction_processor.db_manager.insert_internal_transaction.assert_not_awaited()
        assert transaction_processor.db_manager.insert_transaction_logs.await_count == 2
        transaction_processor.db_manager.insert_transaction_logs.assert_awaited_with(
            **transaction_logs_data.dict(),
        )

    async def test_transaction_fee_correct(self):
        """Test that the transaction fee is calculated correctly in _handle_transaction"""
        # TODO: Implement
        pass

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_no_event_inserted(
        self,
        mock_get_transaction_events,
        transaction_processor,
        contract_config_usdt,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that no event is inserted if no event was found"""
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "TransferFungibleEvent",
            "MintFungibleEvent",
            "BurnFungibleEvent",
        ]
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_get_transaction_events.return_value = []
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        transaction_processor.db_manager.insert_transaction_logs.assert_not_awaited()
        transaction_processor.db_manager.insert_contract_supply_change.assert_not_awaited()
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_not_awaited()
        assert result == set([])

    @patch("app.consumer.tx_processor.get_transaction_events")
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
        transaction_processor,
        contract_config_usdt,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
        request,
    ):
        """Test that no event is inserted if event found but is not in config"""
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = []
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_get_transaction_events.return_value = [
            request.getfixturevalue(event),
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        transaction_processor.db_manager.insert_transaction_logs.assert_not_awaited()
        transaction_processor.db_manager.insert_contract_supply_change.assert_not_awaited()
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_not_awaited()
        assert result == set([])

    @patch("app.consumer.tx_processor.get_transaction_events")
    @pytest.mark.parametrize(
        "event,supply_change,liquidity_change",
        [
            ("transfer_fungible_event", None, None),
            ("transfer_non_fungible_event", None, None),
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
        transaction_processor,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
        request,
    ):
        """Test every event is inserted if event found and is present in config"""
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            request.getfixturevalue(event).__class__.__name__
        ]
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_get_transaction_events.return_value = [
            request.getfixturevalue(event),
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = request.getfixturevalue(event).address
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()
        transaction_processor.db_manager.insert_nft_transfer = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        if supply_change:
            transaction_processor.db_manager.insert_contract_supply_change.assert_awaited_once_with(
                address=request.getfixturevalue(event).address,
                transaction_hash=transaction_data.transaction_hash,
                amount_changed=supply_change,
            )
        else:
            transaction_processor.db_manager.insert_contract_supply_change.assert_not_awaited()
        if liquidity_change:
            transaction_processor.db_manager.insert_pair_liquidity_change.assert_awaited_once_with(
                address=request.getfixturevalue(event).address,
                amount0=liquidity_change[0],
                amount1=liquidity_change[1],
                transaction_hash=transaction_data.transaction_hash,
            )
        else:
            transaction_processor.db_manager.insert_pair_liquidity_change.assert_not_awaited()
        assert result == set([1337])

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_transfer_fungible_to_dead_address_event_inserted(
        self,
        mock_get_transaction_events,
        dead_address,
        transaction_processor,
        contract_config_usdt,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that transfer to dead address is inserted as a log once and as a burn supply change"""
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "TransferFungibleEvent",
            "BurnFungibleEvent",
        ]
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_get_transaction_events.return_value = [
            BurnFungibleEvent(
                address=contract_config_usdt.address,
                log_index=1337,
                value=2000,
            ),
            TransferFungibleEvent(
                address=contract_config_usdt.address,
                log_index=1337,
                src="0xF00D",
                dst=dead_address,
                value=2000,
            ),
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        transaction_processor.db_manager.insert_transaction_logs = AsyncMock()
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        transaction_processor.db_manager.insert_contract_supply_change.assert_awaited_once_with(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            transaction_hash="0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
            amount_changed=-2000,
        )
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_not_awaited()
        assert result == set([1337])

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_transfer_fungible_to_dead_address_event_not_inserted_if_not_in_config(
        self,
        mock_get_transaction_events,
        dead_address,
        transaction_processor,
        contract_config_usdt,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that transfer to dead address is not inserted as a log nor as a supply change event if not in config"""
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = []
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_get_transaction_events.return_value = [
            TransferFungibleEvent(
                address=contract_config_usdt.address,
                log_index=1337,
                src="0xF00D",
                dst=dead_address,
                value=1500,
            ),
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        transaction_processor.db_manager.insert_transaction_logs.assert_not_awaited()
        transaction_processor.db_manager.insert_contract_supply_change.assert_not_awaited()
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_not_awaited()
        assert result == set([])

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_transfer_fungible_from_dead_address_event_inserted(
        self,
        mock_get_transaction_events,
        dead_address,
        transaction_processor,
        contract_config_usdt,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that transfer from dead address is inserted as a log once and as a mint supply change"""
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "TransferFungibleEvent",
            "MintFungibleEvent",
        ]
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_get_transaction_events.return_value = [
            TransferFungibleEvent(
                address=contract_config_usdt.address,
                log_index=1337,
                src=dead_address,
                dst="0xCAFE",
                value=2500,
            ),
            MintFungibleEvent(
                address=contract_config_usdt.address,
                log_index=1337,
                value=1500,
            ),
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        transaction_processor.db_manager.insert_contract_supply_change.assert_awaited_once_with(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            transaction_hash="0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
            amount_changed=1500,
        )
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_not_awaited()
        assert result == set([1337])

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_transfer_fungible_from_dead_address_event_not_inserted_if_not_in_config(
        self,
        mock_get_transaction_events,
        dead_address,
        transaction_processor,
        contract_config_usdt,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that transfer from dead address is not inserted as a log nor as a supply change event if not in config"""
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = []
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_get_transaction_events.return_value = [
            TransferFungibleEvent(
                address=contract_config_usdt.address,
                log_index=1337,
                src=dead_address,
                dst="0xCAFE",
                value=1500,
            )
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        transaction_processor.db_manager.insert_transaction_logs.assert_not_awaited()
        transaction_processor.db_manager.insert_contract_supply_change.assert_not_awaited()
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_not_awaited()
        assert result == set([])

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_mint_pair_event_from_dead_address(
        self,
        mock_get_transaction_events,
        dead_address,
        transaction_processor,
        contract_config_usdt,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that mint pair event from dead address is inserted as log and mint event"""
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = ["MintPairEvent"]
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_get_transaction_events.return_value = [
            MintPairEvent(
                address=contract_config_usdt.address,
                log_index=1337,
                sender=dead_address,
                amount0=1500,
                amount1=2500,
            )
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        transaction_processor.db_manager.insert_contract_supply_change.assert_not_awaited()
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_awaited_once_with(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            amount0=1500,
            amount1=2500,
            transaction_hash="0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
        )
        assert result == set([1337])

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_burn_pair_event_from_dead_address_inserted(
        self,
        mock_get_transaction_events,
        dead_address,
        transaction_processor,
        contract_config_usdt,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that burn pair event to dead address is inserted as log and burn event"""
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = ["BurnPairEvent"]
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_get_transaction_events.return_value = [
            BurnPairEvent(
                address=contract_config_usdt.address,
                log_index=1337,
                src="0xCAFE",
                dst=dead_address,
                amount0=1500,
                amount1=2500,
            )
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        transaction_processor.db_manager.insert_transaction_logs = AsyncMock()
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        transaction_processor.db_manager.insert_contract_supply_change.assert_not_awaited()
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_awaited_once_with(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            amount0=-1500,
            amount1=-2500,
            transaction_hash="0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
        )
        assert result == set([1337])

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_transfer_non_fungible_inserts_nft_transfer(
        self,
        mock_get_transaction_events,
        transaction_processor,
        contract_config_bayc,
        transfer_non_fungible_event,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test TransferNonFungibleEvent is inserted as NFT transfer"""
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = ["TransferNonFungibleEvent"]
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_get_transaction_events.return_value = [
            transfer_non_fungible_event,
        ]
        transaction_receipt_data.logs = [transaction_logs_data]
        contract_mock = Mock()
        contract_mock.address = contract_config_bayc.address
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()
        transaction_processor.db_manager.insert_nft_transfer = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        transaction_processor.db_manager.insert_contract_supply_change.assert_not_awaited()
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_not_awaited()
        transaction_processor.db_manager.insert_nft_transfer.assert_awaited_once_with(
            address="0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
            log_index=1337,
            from_address="0xF00D",
            to_address="0xCAFE",
            token_id=1337,
            transaction_hash=transaction_data.transaction_hash,
        )
        assert result == set([1337])

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_mint_burn_fungible_combination(
        self,
        mock_get_transaction_events,
        transaction_processor,
        burn_fungible_event,
        mint_fungible_event,
        contract_config_usdt,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that multiple mint/burn fungible events together are handled correctly"""
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "MintFungibleEvent",
            "BurnFungibleEvent",
        ]
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_events = [
            burn_fungible_event,
            burn_fungible_event.copy(),
            mint_fungible_event,
            mint_fungible_event.copy(),
            mint_fungible_event.copy(),
        ]
        mock_get_transaction_events.return_value = mock_events
        logs = [transaction_logs_data] * 5
        for i, log in enumerate(logs):
            log.log_index = 1337 + i
            mock_events[i].log_index = 1337 + i
        transaction_receipt_data.logs = logs
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        assert len(result) == 5
        transaction_processor.db_manager.insert_contract_supply_change.assert_awaited_once_with(
            address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            transaction_hash="0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822",
            amount_changed=1500,
        )
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_not_awaited()

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_mint_burn_swap_pair_combination(
        self,
        mock_get_transaction_events,
        transaction_processor,
        burn_pair_event,
        mint_pair_event,
        swap_pair_event,
        contract_config_pair_usdc_weth,
        transaction_data,
        transaction_receipt_data,
        transaction_logs_data,
    ):
        """Test that multiple mint/burn/swap pair events together are handled correctly"""
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "MintPairEvent",
            "BurnPairEvent",
            "SwapPairEvent",
        ]
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        mock_events = [
            burn_pair_event,
            mint_pair_event,
            burn_pair_event.copy(),
            mint_pair_event.copy(),
            swap_pair_event,
            swap_pair_event.copy(),
            mint_pair_event.copy(),
        ]
        mock_get_transaction_events.return_value = mock_events
        logs = [transaction_logs_data] * 7
        for i, log in enumerate(logs):
            log.log_index = 1337 + i
            mock_events[i].log_index = 1337 + i
        transaction_receipt_data.logs = logs
        contract_mock = Mock()
        contract_mock.address = contract_config_pair_usdc_weth.address
        transaction_processor.db_manager.insert_transaction_logs = AsyncMock()
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        assert len(result) == 7
        transaction_processor.db_manager.insert_contract_supply_change.assert_not_awaited()
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_awaited_with(
            address=contract_config_pair_usdc_weth.address,
            amount0=1900,
            amount1=3700,
            transaction_hash=transaction_data.transaction_hash,
        )

    @patch("app.consumer.tx_processor.get_transaction_events")
    async def test_handle_transaction_events_skipped_if_event_addr_not_matching(
        self,
        mock_get_transaction_events,
        transaction_processor,
        transaction_data,
        contract_config_usdt,
        transfer_fungible_event,
        mint_fungible_event,
        burn_fungible_event,
    ):
        """Test that _handle_transaction_events is skipped if event address does not
        match contract address.
        """
        # Arrange
        get_contract_events_mock = Mock()
        get_contract_events_mock.return_value = [
            "TransferFungibleEvent",
            "MintFungibleEvent",
            "BurnFungibleEvent",
        ]
        transaction_processor.contract_parser.get_contract_events = (
            get_contract_events_mock
        )
        transfer_fungible_event.address = "0x1234"
        mint_fungible_event.address = "0x1234"
        burn_fungible_event.address = "0x1234"
        mock_get_transaction_events.return_value = [
            transfer_fungible_event,
            burn_fungible_event,
            mint_fungible_event,
        ]
        contract_mock = Mock()
        contract_mock.address = contract_config_usdt.address
        transaction_processor.db_manager.insert_contract_supply_change = AsyncMock()
        transaction_processor.db_manager.insert_pair_liquidity_change = AsyncMock()
        transaction_processor.db_manager.insert_nft_transfer = AsyncMock()

        # Act
        result = await transaction_processor._handle_transaction_events(
            contract=contract_mock,
            category=Mock(),
            tx_data=transaction_data,
            tx_receipt=Mock(),
        )

        # Assert
        transaction_processor.db_manager.insert_contract_supply_change.assert_not_awaited()
        transaction_processor.db_manager.insert_pair_liquidity_change.assert_not_awaited()
        transaction_processor.db_manager.insert_nft_transfer.assert_not_awaited()
        assert result == set([])


class PartialTransactionProcessor:
    """Tests for PartialTransactionProcessor methods"""

    async def test_consume_partial_unknown_contract_flow(
        self, default_consumer, transaction_data, transaction_receipt_data
    ):
        """Test _consume_partial flow if an unknown contract is encountered"""
        transaction_data.to_address = "0x1234"
        transaction_receipt_data.contract_address = "0x1234"
        default_consumer._handle_contract_creation = AsyncMock()
        default_consumer._handle_transaction = AsyncMock()
        default_consumer._handle_transaction_events = AsyncMock()
        default_consumer.contract_parser.get_contract_category.return_value = None

        await default_consumer._consume_partial(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
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
        _handle_tx_events_mock = AsyncMock()
        _handle_tx_events_mock.return_value = set()
        default_consumer._handle_transaction_events = _handle_tx_events_mock
        default_consumer.contract_parser.get_contract_category.return_value = (
            ContractCategory(contract_config_usdt.category)
        )
        contract_mock = Mock()
        default_consumer.contract_parser.get_contract.return_value = contract_mock
        w3_tx_receipt = Mock()

        await default_consumer._consume_partial(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            w3_tx_receipt=w3_tx_receipt,
        )

        assert default_consumer._n_processed_txs == 1
        default_consumer._handle_contract_creation.assert_not_awaited()
        default_consumer._handle_transaction.assert_awaited_once_with(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            log_indices_to_save=set(),
        )
        default_consumer._handle_transaction_events.assert_awaited_once_with(
            contract=contract_mock,
            category=ContractCategory.ERC20,
            tx_data=transaction_data,
            tx_receipt=w3_tx_receipt,
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
        _handle_tx_events_mock = AsyncMock()
        _handle_tx_events_mock.return_value = set()
        default_consumer._handle_transaction_events = _handle_tx_events_mock
        default_consumer.contract_parser.get_contract_category.return_value = (
            ContractCategory(contract_config_usdt.category)
        )
        contract_mock = Mock()
        default_consumer.contract_parser.get_contract.return_value = contract_mock
        w3_tx_receipt = Mock()

        await default_consumer._consume_partial(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            w3_tx_receipt=w3_tx_receipt,
        )

        default_consumer._handle_transaction.assert_awaited_once_with(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            log_indices_to_save=set(),
        )
        default_consumer._handle_transaction_events.assert_awaited_once_with(
            contract=contract_mock,
            category=ContractCategory.ERC20,
            tx_data=transaction_data,
            tx_receipt=w3_tx_receipt,
        )
        assert default_consumer._n_processed_txs == 1
        default_consumer._handle_contract_creation.assert_awaited_once_with(
            contract=contract_mock,
            tx_data=transaction_data,
            category=ContractCategory.ERC20,
        )


class FullTransactionProcessor:
    """Tests for FullTransactionProcessor methods"""

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
        _handle_tx_events_mock = AsyncMock()
        _handle_tx_events_mock.return_value = set([1337])
        default_consumer._handle_transaction_events = _handle_tx_events_mock
        transaction_receipt_data.logs = [transaction_logs_data]

        await default_consumer._consume_full(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
        )

        default_consumer._handle_transaction.assert_awaited_once_with(
            tx_data=transaction_data,
            tx_receipt_data=transaction_receipt_data,
            log_indices_to_save=set([1337]),
        )
        assert default_consumer._n_processed_txs == 1


class LogFilterTransactionProcessor:
    """Tests for LogFilterTransactionProcessor methods"""

    pass
