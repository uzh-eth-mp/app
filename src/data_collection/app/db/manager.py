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

    async def insert_table_contract(self, address: str, transaction_hash: str):
        """CONTRACT  TABLE"""
        table = f"contract_{self.node_name}"
        address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        transaction_hash = "0xeef10fc5170f669b86c4cd0444882a96087221325f8bf2f55d6188633aa7be7c"

        await self.db.execute(f"""
            INSERT INTO {table} (address, transaction_hash)
            VALUES ({address}, {transaction_hash});
        """)

    async def insert_table_token_contract(self, address: str, symbol: str, name: str, decimals: int, total_supply: int,
                                          token_category: str):
        table = f"token_contract_{self.node_name}"
        address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        symbol = "USDT"
        name = "Tether USD"
        decimals = 6
        total_supply = 12999999994
        token_category = "erc20"

        await self.db.execute(f"""
            INSERT INTO {table} (address, symbol, name, decimals, total_supply, token_category)
            VALUES ({address}, {symbol}, {name}, {decimals}, {total_supply}, {token_category});
        """)

    async def insert_table_contract_supply_change(self, address: str, amount_changed: int, transaction_hash: str):
        table = f"contract_supply_change_{self.node_name}"
        address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        amount_changed = 4524932
        transaction_hash = "0xeef10fc5170f669b86c4cd0444882a96087221325f8bf2f55d6188633aa7be7c"

        await self.db.execute(f"""
            INSERT INTO {table} (address, amount_changed, transaction_changed)
            VALUES ({address}, {amount_changed}, {transaction_hash} );
        """)
        