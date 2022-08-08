-- creating a table func -> https://dba.stackexchange.com/a/42930

-- ERC20 properties -> https://eips.ethereum.org/EIPS/eip-20
-- ERC721 properties -> https://eips.ethereum.org/EIPS/eip-721
-- ERC 1155 properties -> https://eips.ethereum.org/EIPS/eip-1155

-- uint256 data type in postgreSQL as numeric(78,0) -> https://stackoverflow.com/questions/50072618/how-to-create-an-uint256-in-postgresql

-- beware of the python and postgreSQL datatype conventions.
-- in python int32 = 32 bit
-- in postgres int4 = 4 bytes = 32 bit


--address numeric(78,0)PRIMARY KEY NOT NULL,              #uint256
--symbol varchar(128) NOT NULL,
--name varchar(256) NOT NULL,
--decimals int NOT NULL,                                   #int8
--total_supply numeric(78,0) NOT NULL,                     #uint256
--block_timestamp timestamp NOT NULL,                      #without time zone
--block_number bigint NOT NULL,



-- CONTRACT TABLE
-- since not every contract is a token, we create a separate table for all the contract data.
CREATE OR REPLACE FUNCTION contract(blockchain_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       address numeric(78,0) PRIMARY KEY NOT NULL,
       block_timestamp timestamp NOT NULL,
       block_number bigint NOT NULL
      )', blockchain_name || '_contract');
END
$func$;

SELECT contract('bsc');
SELECT contract('eth');
SELECT contract('etc');


-- Create enum type for the tokens category
CREATE TYPE category AS ENUM ('erc20', 'erc271', 'erc1155');

-- TOKEN CONTRACT TABLE - ERC20 & ERC271 & ERC1155
CREATE OR REPLACE FUNCTION token_contract(blockchain_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       address numeric(78,0) PRIMARY KEY REFERENCES %I(address)  NOT NULL,
       symbol varchar(128),
       name varchar(256),
       decimals int,
       total_supply numeric(78,0),
       token_category category
      )', blockchain_name || '_token_contract', blockchain_name || '_contract');
END
$func$;

SELECT token_contract('eth');
SELECT token_contract('bsc');
SELECT token_contract('etc');


--CONTRACT SUPPLY CHANGE TABLE
CREATE OR REPLACE FUNCTION contract_supply_change(blockchain_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I(
       address numeric(78,0)  NOT NULL,
       amount_changed numeric(78,0) NOT NULL,
       block_timestamp timestamp NOT NULL,
       transaction_hash varchar(256) NOT NULL,
       PRIMARY KEY(address, block_timestamp),
       FOREIGN KEY(address)
       REFERENCES %I(address)
      )', blockchain_name || '_contract_supply_change', blockchain_name || '_token_contract');
END
$func$;

SELECT contract_supply_change('eth');
SELECT contract_supply_change('bsc');
SELECT contract_supply_change('etc');







