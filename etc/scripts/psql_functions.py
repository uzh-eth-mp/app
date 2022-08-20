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

    # disconnect after we're done
    await manager.disconnect()

asyncio.run(main())
