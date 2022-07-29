import asyncpg

from app import init_logger


log = init_logger(__name__)


class DatabaseManager:
    """
    Manage the PostgreSQL connection and CRUD operations.

    https://magicstack.github.io/asyncpg/current/usage.html
    """

    def __init__(self, postgresql_dsn: str, node_name: str) -> None:
        """
        Args:
            postgresql_dsn: connection arguments in URI format
                            e.g. postgres://user:password@host:port/database
            node_name: the type of the node (eth, etc, bsc), selects matching
                        tables for all operations
        """
        self.dsn: str = postgresql_dsn
        self.node_name = node_name
        self.db: asyncpg.Connection = None

    async def connect(self):
        """Connects to the PostgreSQL database."""
        self.db = await asyncpg.connect(
            dsn=self.dsn
        )
        log.info("Connected to PostgreSQL")

    async def disconnect(self):
        """Disconnect from PostgreSQL"""
        await self.db.close()
        log.info("Disconnected from PostgreSQL")

    async def insert_block_data(self):
        """
        Insert block data into the database
        """
        # TODO: Update this method with valid block data given
        # from the arguments
        table = f"block_data_{self.node_name}"
        hash = "0xb2fb6a01624f285604913697f0f80c8ee86620750be532cc3dc5751cf079662e"
        difficulty = "12,120,825,516,066,787"
        gas_limit = "29,970,705"

        await self.db.execute(f"""
            INSERT INTO {table} (hash, difficulty, gas_limit)
            VALUES ($1, $2, $3);
        """, hash, difficulty, gas_limit)
