import asyncio
import pathlib
import sys

# Don't remove, ensures that the import of DatabaseManager works
current_dir_path = pathlib.Path(__file__).parent.parent.parent
app_module_path = pathlib.Path(current_dir_path / pathlib.Path("src/data_collection")).resolve()
sys.path.insert(0, str(app_module_path))

from app.db.manager import DatabaseManager

async def main():
    # Connect to DB
    manager = DatabaseManager(
        postgresql_dsn="postgres://user:postgres@localhost:5432/db",
        node_name="eth"
    )
    await manager.connect()

    # Code you want to test goes below
    # e.g.   await manager.insert_block_data()
    await manager.insert_contract(
        address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
        transaction_hash="0x871dadd3f5ca95b398575d710d39385de9123a10717e2e37a90545a805daca77"
    )

    await manager.insert_token_contract(
        address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
        symbol="USDT",
        name="Tether",
        decimals=6,
        total_supply=1000000,
        token_category="erc20"
    )

    await manager.insert_contract_supply_change(
        address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
        amount_changed=22,
        transaction_hash="0x871dadd3f5ca95b398575d710d39385de9123a10717e2e37a90545a805daca78"
    )

    # disconnect after we're done
    await manager.disconnect()

asyncio.run(main())
