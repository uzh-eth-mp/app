import asyncio
import os
from datetime import datetime
from typing import Any

import pytest
import pytest_asyncio


from app.db.manager import DatabaseManager

@pytest.fixture(scope="session")
def event_loop():
    """
    Note:
        event_loop is function scoped by default, use this method
        (session scope) to avoid a ScopeMismatch exception
    """
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="session")
async def db_manager():
    # Get postgres dsn
    host = os.environ.get("POSTGRES_HOST")
    port = os.environ.get("POSTGRES_PORT")
    user = os.environ.get("POSTGRES_USER")
    pw = os.environ.get("POSTGRES_PASSWORD")
    db_name = os.environ.get("POSTGRES_DB")
    db_dsn = f"postgresql://{user}:{pw}@{host}:{port}/{db_name}"
    db_manager = DatabaseManager(
        postgresql_dsn=db_dsn,
        node_name="eth"
    )
    # Connect to the db
    await db_manager.connect()

    yield db_manager

    await db_manager.disconnect()


@pytest_asyncio.fixture
async def clean_db(db_manager):
    """
    Remove data from all tables. This fixture has a 'function' scope so
    it is executed before every test.
    """
    # Get all table names
    table_names = await db_manager.db.fetch(
        """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_type='BASE TABLE';
        """
    )
    # Remove all records inside those tables
    #query_args = ",".join([ f"${i+1}" for i in range(len(table_names)) ])
    query_args = ", ".join(list(map(lambda n: n["table_name"], table_names)))
    await db_manager.db.execute(
        f"TRUNCATE {query_args};"
    )


shared_tx_hash = "0xa76bef720a7093e99ce5532988623aaf62b490ecba52d1a94cb6e118ccb56822"
shared_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

@pytest.fixture
def block_data() -> dict[str, Any]:
    return dict(
        block_number=10,
        block_hash="0x98bdfb36d9d0d259afa8403b62255e0c04161a341a2aa646dbeae6d1c32dcb9d",
        nonce="0x8aee4c3380578665",
        difficulty=76543786543216789,
        gas_limit=30029295,
        gas_used=30025828,
        timestamp=datetime.fromtimestamp(1661048118),
        miner="0xea674fdde714fd979de3edf0f56aa9716b898ec8",
        parent_hash="0x3d1131b702e9aa071fb15970b4271cde104e5802b542f478782f5b1ef0ffa436",
        block_reward=2.052229489633251327
    )


@pytest.fixture
def transaction_data() -> dict[str, Any]:
    return dict(
        transaction_hash=shared_tx_hash,
        block_number=10,
        from_address="0xca44f331c32783cc6678cb5ffaa2b6739299b42b",
        to_address="0xd26a2ba4472a50ea23bef8189a3de4911af03dad",
        value=0.000000487343799995,
        transaction_fee=0.000048247036173,
        gas_price=.000000002297477913,
        gas_limit=21000,
        gas_used=21000,
        is_token_tx=False,
        input_data="0x"
    )


@pytest.fixture
def internal_transaction_data() -> dict[str, Any]:
    return dict(
        transaction_hash=shared_tx_hash,
        from_address="0xca44f331c32783cc6678cb5ffaa2b6739299b42b",
        to_address="0xd26a2ba4472a50ea23bef8189a3de4911af03dad",
        value=.000000487343799995,
        gas_price=.000000002297477913,
        gas_limit=21000,
        gas_used=21000,
        input_data="xd",
        function_type="CREATE"
    )


@pytest.fixture
def transaction_logs_data() -> dict[str, Any]:
    return dict(
        transaction_hash=shared_tx_hash,
        address="0xf76de79a8cb78158f22dc8e0f3b6f3f6b9cd97d8",
        log_index=0,
        data="|Â¦E<",
        removed=False,
        topics=[
            "0x940c4b3549ef0aaff95807dc27f62d88ca15532d1bf535d7d63800f40395d16c",
            "0x000000000000000000000000e2de6d17b8314f7f182f698606a53a064b00ddcc",
            "0x0000000000000000000000005e42c86bb5352e9d985dd1200e05a35f4b0b2b14",
            "0x54494d4500000000000000000000000000000000000000000000000000000000"
        ]
    )

@pytest.fixture
def contract_data() -> dict[str, Any]:
    return dict(
        address=shared_address,
        transaction_hash="0x871dadd3f5ca95b398575d710d39385de9123a10717e2e37a90545a805daca77"
    )

@pytest.fixture
def token_contract_data() -> dict[str, Any]:
    return dict(
        address=shared_address,
        symbol="USDT",
        name="Tether",
        decimals=6,
        total_supply=1000000,
        token_category="erc20"
    )

@pytest.fixture
def contract_supply_change_data() -> dict[str, Any]:
    return dict(
        address=shared_address,
        amount_changed=22,
        transaction_hash="0x871dadd3f5ca95b398575d710d39385de9123a10717e2e37a90545a805daca78"
    )