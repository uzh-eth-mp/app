from unittest.mock import AsyncMock

from app.model.transaction import InternalTransactionData


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

    async def test_no_event_inserted(self):
        """Test that no event is inserted if no event was found"""
        # TODO: Implement
        pass

    async def test_no_event_inserted_if_not_in_config(self):
        """Test that no event is inserted if event found but is not in config"""
        # TODO: Implement
        pass

    async def test_transfer_fungible_event_inserted(self):
        """Test that transfer fungible event is inserted"""
        # TODO: Implement
        pass

    async def test_transfer_fungible_event_not_inserted_if_not_in_config(self):
        """Test that transfer fungible event is not inserted if not in config"""
        # TODO: Implement
        pass

    async def test_mint_fungible_event_inserted(self):
        """Test that mint fungible event is inserted"""
        # TODO: Implement
        pass

    async def test_mint_fungible_event_not_inserted_if_not_in_config(self):
        """Test that mint fungible event is not inserted if not in config"""
        # TODO: Implement
        pass

    async def test_burn_fungible_event_inserted(self):
        """Test that burn fungible event is inserted"""
        # TODO: Implement
        pass

    async def test_burn_fungible_event_not_inserted_if_not_in_config(self):
        """Test that burn fungible event is not inserted if not in config"""
        # TODO: Implement
        pass

    async def test_transfer_fungible_to_dead_address_event_inserted(self):
        """Test that transfer to dead address is inserted as a log once and as a burn supply change"""
        # TODO: Implement
        pass

    async def test_transfer_fungible_to_dead_address_event_not_inserted_if_not_in_config(
        self,
    ):
        """Test that transfer to dead address is not inserted as a log nor as a supply change event if not in config"""
        # TODO: Implement
        pass

    async def test_transfer_fungible_from_dead_address_event_inserted(self):
        """Test that transfer from dead address is inserted as a log once and as a mint supply change"""
        # TODO: Implement
        pass

    async def test_transfer_fungible_from_dead_address_event_not_inserted_if_not_in_config(
        self,
    ):
        """Test that transfer from dead address is not inserted as a log nor as a supply change event if not in config"""
        # TODO: Implement
        pass

    async def test_mint_pair_event_inserted(self):
        """Test that mint pair event is inserted"""
        # TODO: Implement
        pass

    async def test_mint_pair_event_not_inserted_if_not_in_config(self):
        """Test that mint pair event is not inserted if not in config"""
        # TODO: Implement
        pass

    async def test_burn_pair_event_inserted(self):
        """Test that burn pair event is inserted"""
        # TODO: Implement
        pass

    async def test_burn_pair_event_not_inserted_if_not_in_config(self):
        """Test that burn pair event is not inserted if not in config"""
        # TODO: Implement
        pass

    async def test_swap_pair_event_inserted(self):
        """Test that swap pair event is inserted"""
        # TODO: Implement
        pass

    async def test_swap_pair_event_not_inserted_if_not_in_config(self):
        """Test that swap pair event is not inserted if not in config"""
        # TODO: Implement
        pass


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
