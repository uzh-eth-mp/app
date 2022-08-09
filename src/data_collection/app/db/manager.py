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

    async def insert_block_data(self, block_number: int, block_hash: str, nonce: str, difficulty: int,
                                 gas_limit: int, gas_used: int, timestamp: str, miner: str, parent_hash: str, 
                                 omner_hash: str, block_reward: float, uncles_reward: float ):
        """
        Insert block data into the database
        """

        table = f"block_data_{self.node_name}"

        await self.db.execute(f"""
            INSERT INTO {table} (block_number, block_hash, nonce, difficulty, gas_limit, gas_used, timestamp, miner, parent_hash, omner_hash, block_reward, uncles_reward)
            VALUES ($1, $2, $3,$4, $5, $6,$7,$8, $9, $10, $11, $12);
        """, block_number, block_hash, nonce, difficulty, gas_limit, gas_used, timestamp,  miner,
             parent_hash, omner_hash, block_reward, uncles_reward)

    
    async def insert_transaction_data(self, transaction_hash: str, block_number: int, from_address: str, to_address: str, value: float, transaction_fee: float,
                                      gas_price: float, gas_limit: int, gas_used: int, is_token_tx: bool, input_data: str):
        """
        Insert transaction data into the database
        """

        table = f"transaction_data_{self.node_name}"

        await self.db.execute(f"""
            INSERT INTO {table} (transaction_hash, block_number, from_address, to_address, value, transaction_fee, gas_price, gas_limit, gas_used, is_token_tx, input_data)
            VALUES ($1, $2, $3,$4, $5, $6,$7,$8, $9, $10, $11);
        """, transaction_hash, block_number, from_address, to_address, value, transaction_fee, gas_price, gas_limit, gas_used, is_token_tx, input_data)

    async def insert_internal_transaction_data(self, transaction_hash: str, block_number: int, from_address: str, to_address: str, value: float, transaction_fee: float,
                                      gas_price: float, gas_limit: int, gas_used: int, is_token_tx: bool, input_data: str):
        """
        Insert transaction data into the database
        """

        table = f"internal_transaction_data_{self.node_name}"

        await self.db.execute(f"""
            INSERT INTO {table} (transaction_hash, block_number, from_address, to_address, value, transaction_fee, gas_price, gas_limit, gas_used, is_token_tx, input_data)
            VALUES ($1, $2, $3,$4, $5, $6,$7,$8, $9, $10, $11);
        """, transaction_hash, block_number, from_address, to_address, value, transaction_fee, gas_price, gas_limit, gas_used, is_token_tx, input_data)


    async def insert_transaction_log_data(self, unique_id: int, transaction_hash: str, address: str, log_index: int, data: str, block_hash: str, block_number: int, removed: bool, topics: list[str]):
        """
        Insert transaction data into the database
        """

        table = f"transaction_log_data_{self.node_name}"
       
        await self.db.execute(f"""
            INSERT INTO {table} (transaction_hash, address, log_index, data, black_hash, block_number, removed, topics)
            VALUES ($1, $2, $3,$4, $5, $6,$7,$8, $9);
        """, transaction_hash, address, log_index, data, block_hash, block_number, removed, topics)

    