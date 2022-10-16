-- creating a table func -> https://dba.stackexchange.com/a/42930

-- ERC20 properties -> https://eips.ethereum.org/EIPS/eip-20
-- ERC721 properties -> https://eips.ethereum.org/EIPS/eip-721
-- ERC 1155 properties -> https://eips.ethereum.org/EIPS/eip-1155

-- uint256 data type in postgreSQL as numeric(78,0) -> https://stackoverflow.com/questions/50072618/how-to-create-an-uint256-in-postgresql
-- but we agreed on varchar(256) for address.

-- beware of the python and postgreSQL datatype conventions.
-- in python int32 = 32 bit
-- in postgres int4 = 4 bytes = 32 bit


--address varchar(256)PRIMARY KEY NOT NULL,              #uint256
--symbol varchar(128) NOT NULL,
--name varchar(256) NOT NULL,
--decimals int NOT NULL,                                   #int8
--total_supply numeric(78,0) NOT NULL,                     #uint256
--block_timestamp timestamp NOT NULL,                      #without time zone
--block_number bigint NOT NULL,



-- CONTRACT TABLE
-- since not every contract is a token, we create a separate table for all the contract data.
CREATE OR REPLACE FUNCTION create_table_contract(blockchain_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       address varchar(256) PRIMARY KEY NOT NULL,
       transaction_hash varchar(256) NOT NULL,
       is_pair_contract boolean NOT NULL
      )', blockchain_name || '_contract');
END
$func$;

SELECT create_table_contract('bsc');
SELECT create_table_contract('eth');
SELECT create_table_contract('etc');


-- Create enum type for the tokens category
CREATE TYPE token_category AS ENUM ('erc20', 'erc721', 'erc1155');

-- TOKEN CONTRACT TABLE - ERC20 & ERC721 & ERC1155
CREATE OR REPLACE FUNCTION create_table_token_contract(blockchain_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       address varchar(256) PRIMARY KEY REFERENCES %I(address) NOT NULL,
       symbol varchar(128),
       name varchar(256),
       decimals int,
       total_supply numeric(78,0),
       token_category token_category
      )', blockchain_name || '_token_contract', blockchain_name || '_contract');
END
$func$;

SELECT create_table_token_contract('eth');
SELECT create_table_token_contract('bsc');
SELECT create_table_token_contract('etc');


--CONTRACT SUPPLY CHANGE TABLE
CREATE OR REPLACE FUNCTION create_table_contract_supply_change(blockchain_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I(
       address varchar(256) REFERENCES %I(address) NOT NULL,
       amount_changed numeric(78,0) NOT NULL,
       transaction_hash varchar(256) NOT NULL,
       PRIMARY KEY(address, transaction_hash)
   )', blockchain_name || '_contract_supply_change', blockchain_name || '_token_contract');
END
$func$;

SELECT create_table_contract_supply_change('eth');
SELECT create_table_contract_supply_change('bsc');
SELECT create_table_contract_supply_change('etc');


---PAIR CONTRACT TABLE---
CREATE OR REPLACE FUNCTION create_table_pair_contract(blockchain_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I(
       address varchar(256) PRIMARY KEY REFERENCES %I(address) NOT NULL,
       token0_address varchar(256) NOT NULL,
       token1_address varchar(256) NOT NULL,
       reserve0 numeric(78,0) NOT NULL,
       reserve1 numeric(78,0) NOT NULL, 
       factory varchar(256) NOT NULL
   )', blockchain_name || '_pair_contract', blockchain_name || '_contract');
END
$func$;

SELECT create_table_pair_contract('eth');
SELECT create_table_pair_contract('bsc');
SELECT create_table_pair_contract('etc');


--CONTRACT SUPPLY CHANGE TABLE
CREATE OR REPLACE FUNCTION create_table_pair_liquidity_change(blockchain_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I(
       address varchar(256) REFERENCES %I(address) NOT NULL,
       amount0 numeric(78,0) NOT NULL,
       amount1 numeric(78,0) NOT NULL,
       transaction_hash varchar(256) NOT NULL,
       PRIMARY KEY(address, transaction_hash)
   )', blockchain_name || '_pair_liquidity_change', blockchain_name || '_pair_contract');
END
$func$;

SELECT create_table_pair_liquidity_change('eth');
SELECT create_table_pair_liquidity_change('bsc');
SELECT create_table_pair_liquidity_change('etc');