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

    async def insert_table_contract_data(self):
        """CONTRACT DATA TABLE"""
        table = f"contract_data_{self.node_name}"
        contract_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        bytecode = "0x6060604052600436106100b95763ffffffff7c010000000000000000000000000000000000000000000000000000000" \
                   "060003504166306fdde0381146100be578063095ea7b31461014857806318160ddd1461017e57806323b872dd146101a3" \
                   "578063313ce567146101cb57806342966c68146101f457806370a082311461020a57806379cc67901461022957806395d" \
                   "89b411461024b578063a9059cbb1461025e578063cae9ca5114610282578063dd62ed3e146102e7575b600080fd5b3415" \
                   "6100c957600080fd5b6100d161030c565b604051602080825281908101838181518152602001915080519060200190808" \
                   "38360005b8381101561010d5780820151838201526020016100f5565b50505050905090810190601f16801561013a5780" \
                   "820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561015357600080f" \
                   "d5b61016a600160a060020a03600435166024356103aa565b604051901515815260200160405180910390f35b34156101" \
                   "8957600080fd5b6101916103da565b60405190815260200160405180910390f35b34156101ae57600080fd5b61016a600" \
                   "160a060020a03600435811690602435166044356103e0565b34156101d657600080fd5b6101de610457565b60405160ff" \
                   "909116815260200160405180910390f35b34156101ff57600080fd5b61016a600435610460565b341561021557600080f" \
                   "d5b610191600160a060020a03600435166104eb565b341561023457600080fd5b61016a600160a060020a036004351660" \
                   "24356104fd565b341561025657600080fd5b6100d16105d9565b341561026957600080fd5b610280600160a060020a036" \
                   "0043516602435610644565b005b341561028d57600080fd5b61016a60048035600160a060020a03169060248035919060" \
                   "649060443590810190830135806020601f820181900481020160405190810160405281815292919060208401838380828" \
                   "4375094965061065395505050505050565b34156102f257600080fd5b610191600160a060020a03600435811690602435" \
                   "16610785565b60008054600181600116156101000203166002900480601f0160208091040260200160405190810160405" \
                   "280929190818152602001828054600181600116156101000203166002900480156103a25780601f106103775761010080" \
                   "83540402835291602001916103a2565b820191906000526020600020905b8154815290600101906020018083116103855" \
                   "7829003601f168201915b505050505081565b600160a060020a0333811660009081526005602090815260408083209386" \
                   "16835292905220819055600192915050565b60035481565b600160a060020a03808416600090815260056020908152604" \
                   "08083203390941683529290529081205482111561041557600080fd5b600160a060020a03808516600090815260056020" \
                   "9081526040808320339094168352929052208054839003905561044d8484846107a2565b5060019392505050565b60025" \
                   "460ff1681565b600160a060020a0333166000908152600460205260408120548290101561048657600080fd5b600160a0" \
                   "60020a03331660008181526004602052604090819020805485900390556003805485900390557fcc16f5dbb4873280815" \
                   "c1ee09dbd06736cffcc184412cf7a71a0fdb75d397ca59084905190815260200160405180910390a2506001919050565b" \
                   "60046020526000908152604090205481565b600160a060020a03821660009081526004602052604081205482901015610" \
                   "52357600080fd5b600160a060020a03808416600090815260056020908152604080832033909416835292905220548211" \
                   "1561055657600080fd5b600160a060020a038084166000818152600460209081526040808320805488900390556005825" \
                   "280832033909516835293905282902080548590039055600380548590039055907fcc16f5dbb4873280815c1ee09dbd06" \
                   "736cffcc184412cf7a71a0fdb75d397ca59084905190815260200160405180910390a250600192915050565b600180546" \
                   "00181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001" \
                   "828054600181600116156101000203166002900480156103a25780601f106103775761010080835404028352916020019" \
                   "16103a2565b61064f3383836107a2565b5050565b60008361066081856103aa565b1561077d5780600160a060020a0316" \
                   "638f4ffcb1338630876040518563ffffffff167c010000000000000000000000000000000000000000000000000000000" \
                   "00281526004018085600160a060020a0316600160a060020a0316815260200184815260200183600160a060020a031660" \
                   "0160a060020a0316815260200180602001828103825283818151815260200191508051906020019080838360005b83811" \
                   "0156107165780820151838201526020016106fe565b50505050905090810190601f168015610743578082038051600183" \
                   "6020036101000a031916815260200191505b5095505050505050600060405180830381600087803b15156107645760008" \
                   "0fd5b6102c65a03f1151561077557600080fd5b505050600191505b509392505050565b60056020908152600092835260" \
                   "4080842090915290825290205481565b6000600160a060020a03831615156107b957600080fd5b600160a060020a03841" \
                   "6600090815260046020526040902054829010156107df57600080fd5b600160a060020a03831660009081526004602052" \
                   "60409020548281011161080557600080fd5b50600160a060020a038083166000818152600460205260408082208054948" \
                   "8168084528284208054888103909155938590528154870190915591909301927fddf252ad1be2c89b69c2b068fc378daa" \
                   "952ba7f163c4a11628f55a4df523b3ef9085905190815260200160405180910390a3600160a060020a038084166000908" \
                   "152600460205260408082205492871682529020540181146108a257fe5b505050505600a165627a7a72305820604ef788" \
                   "ac8abdaedc46b8f7086ffceec1d1e365e29400b7d236b16d049806500029"
        block_timestamp = 1478431966
        block_number = 18

        await self.db.execute(f"""
            INSERT INTO {table} (contract_address, bytecode, block_timestamp, block_number)
            VALUES ({contract_address}, {bytecode}, {block_timestamp}, {block_number});
        """)

    async def insert_table_token_contract_data_erc20(self):
        """ERC20"""
        erc_type = "erc20"
        table = f"token_contract_data_{self.node_name}_{erc_type}"
        contract_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        symbol = "USDT"
        name = "Tether USD"
        decimals = 6
        total_supply = 12999999994
        block_timestamp = 1478431966
        block_number = 18

        await self.db.execute(f"""
            INSERT INTO {table} (contract_address, symbol, name, decimals, total_supply, block_timestamp, block_number)
            VALUES ({contract_address}, {symbol}, {name}, {decimals}, {total_supply}, {block_timestamp}, {block_number});
        """)

    async def insert_table_token_contract_data_erc271(self):
        """ERC271"""
        erc_type = "erc271"
        table = f"token_contract_data_{self.node_name}_{erc_type}"
        contract_address = "0x06012c8cf97BEaD5deAe237070F9587f8E7A266d"
        symbol = "USDT"
        name = "CK"
        decimals = 0
        total_supply = 65610
        block_timestamp = 1478431965
        block_number = 15

        await self.db.execute(f"""
            INSERT INTO {table} (contract_address, symbol, name, decimals, total_supply, block_timestamp, block_number)
            VALUES ({contract_address}, {symbol}, {name}, {decimals}, {total_supply}, {block_timestamp}, {block_number});
        """)

    async def insert_table_token_contract_data_erc1155(self):
        """ERC1155"""
        erc_type = "erc1155"
        table = f"token_contract_data_{self.node_name}_{erc_type}"
        contract_address = "0x1ca3262009b21F944e6b92a2a88D039D06F1acFa"
        total_supply = 65610
        block_timestamp = 1478431963
        block_number = 14

        await self.db.execute(f"""
            INSERT INTO {table} (contract_address, total_supply, block_timestamp, block_number)
            VALUES ({contract_address}, {total_supply}, {block_timestamp}, {block_number});
        """)