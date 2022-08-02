-- creating a table -> https://dba.stackexchange.com/a/42930

-- ERC20 properties -> https://eips.ethereum.org/EIPS/eip-20
-- ERC721 properties -> https://eips.ethereum.org/EIPS/eip-721
-- ERC 1155 properties -> https://eips.ethereum.org/EIPS/eip-1155

-- uint256 data type in postgreSQL as numeric(78,0) -> https://stackoverflow.com/questions/50072618/how-to-create-an-uint256-in-postgresql

-- beware of the python and postgreSQL datatype conventions.
-- in python int32 = 32 bit
-- in postgres int4 = 4 bytes = 32 bit


CREATE OR REPLACE FUNCTION create_table_token_contract_data(token_name varchar(30))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       contract id PRIMARY KEY NOT NULL,
       address numeric(78,0) NOT NULL,       #uint256
       symbol varchar(128) NOT NULL,
       name varchar(256) NOT NULL,
       decimals int NOT NULL,                #int8
       total_supply numeric(78,0) NOT NULL,  #uint256
       block_timestamp timestamp NOT NULL,   #without time zone
       block_number bigint NOT NULL,
      )', 'block_data_' || token_name);
END
$func$;

SELECT create_table_block_data('ERC20');
SELECT create_table_block_data('ERC271');


-- ERC1155
CREATE TABLE ERC1151(
       contract id PRIMARY KEY NOT NULL,
       address numeric(78,0) NOT NULL,       #uint256
       decimals int NOT NULL,                #int8
       total_supply numeric(78,0) NOT NULL,  #uint256
       block_timestamp timestamp NOT NULL,   #without time zone
       block_number bigint NOT NULL,
);


-- since not every contract is a token, we create a separate table for the contract data.
 CREATE TABLE CONTRACT_DATA(
       contract id PRIMARY KEY NOT NULL,
       bytecode bytea NOT NULL, ###### I AM NOT SURE IF ALL CONTRACTS HAVE IT ###
       block_timestamp timestamp NOT NULL,
       block_number bigint
);