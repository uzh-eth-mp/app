import asyncio
import pathlib
import sys

from app.db.manager import DatabaseManager

# Don't remove, ensures that the import of DatabaseManager works
current_dir_path = pathlib.Path(__file__).parent.parent.parent
app_module_path = pathlib.Path(current_dir_path / pathlib.Path("src/data_collection")).resolve()
sys.path.insert(0, str(app_module_path))

async def main():
    # Connect to DB
    manager = DatabaseManager(
        postgresql_dsn="postgres://user:postgres@localhost:5432/db",
        node_name="eth"
    )
    await manager.connect()

    # Code you want to test goes below
    await manager.insert_table_token_contract(...)

    # disconnect after we're done
    await manager.disconnect()

asyncio.run(main())
