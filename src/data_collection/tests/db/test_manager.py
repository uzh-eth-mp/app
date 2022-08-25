import pytest
from asyncpg.exceptions import (
    ForeignKeyViolationError,
    UniqueViolationError
)


class TestInsert:
    """Tests for `INSERT INTO <table> VALUES ...`"""

    @pytest.mark.usefixtures("clean_db")
    async def test_insert_block(self, db_manager, block_data):
        """Test insert of block data"""
        await db_manager.insert_block(**block_data)

    @pytest.mark.usefixtures("clean_db")
    async def test_insert_block_raises_pk_error(self, db_manager, block_data):
        """Test insert of block data"""
        await db_manager.insert_block(**block_data)
        with pytest.raises(UniqueViolationError):
            await db_manager.insert_block(**block_data)

    @pytest.mark.usefixtures("clean_db")
    async def test_insert_transaction(self, db_manager, block_data, transaction_data):
        """Test insert of transaction data"""
        # Need to insert a block first to satisfy the FK constraint
        await db_manager.insert_block(**block_data)
        await db_manager.insert_transaction(**transaction_data)

    @pytest.mark.usefixtures("clean_db")
    async def test_insert_transaction_raises_fk_error(
        self, db_manager, block_data, transaction_data
    ):
        """Test insert of transaction data without matching block number"""
        with pytest.raises(ForeignKeyViolationError):
            await db_manager.insert_transaction(**transaction_data)

    @pytest.mark.usefixtures("clean_db")
    async def test_insert_internal_transaction(
        self, db_manager, block_data, transaction_data, internal_transaction_data
    ):
        """Test insert of internal transaction"""
        await db_manager.insert_block(**block_data)
        await db_manager.insert_transaction(**transaction_data)
        await db_manager.insert_internal_transaction(**internal_transaction_data)

    @pytest.mark.usefixtures("clean_db")
    async def test_insert_contract(
        self, db_manager, contract_data
    ):
        """Test insert of contract data"""
        await db_manager.insert_contract(**contract_data)

    @pytest.mark.usefixtures("clean_db")
    @pytest.mark.parametrize("token_category", ["erc20", "erc721", "erc1155"])
    async def test_insert_token_contract(
        self, db_manager, contract_data, token_contract_data, token_category
    ):
        """Test insert of token contract data"""
        # Need to insert contract data first
        await db_manager.insert_contract(**contract_data)
        # Then insert *token* contract data
        token_contract_data["token_category"] = token_category
        await db_manager.insert_token_contract(**token_contract_data)

    @pytest.mark.usefixtures("clean_db")
    @pytest.mark.parametrize("amount", [20, -30, 0])
    async def test_insert_contract_supply_change_data(
        self, db_manager, contract_data, token_contract_data,
        contract_supply_change_data, amount
    ):
        """Test insert of contract supply change data"""
        await db_manager.insert_contract(**contract_data)
        await db_manager.insert_token_contract(**token_contract_data)
        contract_supply_change_data["amount_changed"] = amount
        await db_manager.insert_contract_supply_change(
            **contract_supply_change_data
        )
