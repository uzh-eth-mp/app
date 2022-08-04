-- creating a table func -> https://dba.stackexchange.com/a/42930

-- ERC20 properties -> https://eips.ethereum.org/EIPS/eip-20
-- ERC721 properties -> https://eips.ethereum.org/EIPS/eip-721
-- ERC 1155 properties -> https://eips.ethereum.org/EIPS/eip-1155

-- uint256 data type in postgreSQL as numeric(78,0) -> https://stackoverflow.com/questions/50072618/how-to-create-an-uint256-in-postgresql

-- beware of the python and postgreSQL datatype conventions.
-- in python int32 = 32 bit
-- in postgres int4 = 4 bytes = 32 bit



-- CONTRACT DATA TABLE
-- since not every contract is a token, we create a separate table for all the contract data.
CREATE OR REPLACE FUNCTION create_table_contract_data(blockchain_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (blockchain_name varchar(30))
       contract_address numeric(78,0) PRIMARY KEY NOT NULL,      #uint256
       bytecode bytea,
       block_timestamp timestamp NOT NULL,
       block_number bigint
      )', 'contract_data_'  || blockchain_name);
END
$func$;

SELECT create_table_contract_data('bsc');
SELECT create_table_contract_data('eth');
SELECT create_table_contract_data('etc');


-- TOKEN CONTRACT DATA TABLE - ERC20 & ERC271
CREATE OR REPLACE FUNCTION create_table_token_contract_data(blockchain_name varchar(30),token_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       contract_address numeric(78,0)PRIMARY KEY NOT NULL,      #uint256
       symbol varchar(128) NOT NULL,
       name varchar(256) NOT NULL,
       decimals int NOT NULL,                                   #int8
       total_supply numeric(78,0) NOT NULL,                     #uint256
       block_timestamp timestamp NOT NULL,                      #without time zone
       block_number bigint NOT NULL,
       CONSTRAINT fk_contract_address
         FOREIGN KEY (contract_address)
            REFERENCES %I(contract_address)
      )', 'token_contract_data_' || blockchain_name || '_' || token_name, 'contract_data_' || blockchain_name);
END
$func$;

SELECT create_table_token_contract_data('eth', 'erc20');
SELECT create_table_token_contract_data('bsc', 'erc20');
SELECT create_table_token_contract_data('etc', 'erc20');
SELECT create_table_token_contract_data('bsc', 'erc271');
SELECT create_table_token_contract_data('eth', 'erc271');
SELECT create_table_token_contract_data('etc', 'erc271');


--TOKEN CONTRACT DATA TABLE - ERC1155
CREATE OR REPLACE FUNCTION create_table_token_contract_data_erc1155(blockchain_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (blockchain_name varchar(30))
       contract_address numeric(78,0)PRIMARY KEY NOT NULL,       #uint256
       decimals int NOT NULL,                                    #int8
       total_supply numeric(78,0) NOT NULL,                      #uint256
       block_timestamp timestamp NOT NULL,                       #without time zone
       block_number bigint NOT NULL,
       CONSTRAINT fk_contract_address
         FOREIGN KEY (contract_address)
            REFERENCES %I(contract_address)
      )', 'token_contract_data_'  || blockchain_name || '_erc1155', 'contract_data_'  || blockchain_name);
END
$func$;

SELECT create_table_token_contract_data_erc1155('bsc');
SELECT create_table_token_contract_data_erc1155('eth');
SELECT create_table_token_contract_data_erc1155('etc');

