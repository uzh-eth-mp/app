-- https://dba.stackexchange.com/a/42930

CREATE OR REPLACE FUNCTION create_table_block_data(node_name varchar(3))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       number_serial PRIMARY KEY NOT NULL,
       block_hash varchar(256) NOT NULL,
       difficulty numeric(78,0) NOT NULL,
       gas_limit bigint NOT NULL,
       gas_used bigint NOT NULL,
       timestamp timestamp NOT NULL,
       miner varchar(256) NOT NULL,
       parent_hash varchar(256) NOT NULL,
       omner_hash varchar(256) NOT NULL,
       block_reward numeric(78,18) NOT NULL,
       uncles_reward, numeric(78,18) NOT NULL
      )', 'block_data_' || node_name);
END
$func$;

SELECT create_table_block_data('eth');
SELECT create_table_block_data('etc');
SELECT create_table_block_data('bsc');


CREATE OR REPLACE FUNCTION create_table_transaction_data(node_name varchar(3))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       unique_id PRIMARY KEY NOT NULL,
       transaction_hash varchar(256),
       block_number bigint NOT NULL,
       timestamp timestamp NOT NULL,
       from_address varchar(256) NOT NULL,
       to_address varchar(256) NOT NULl
       value numeric(78,0) NOT NULL,
       transaction_fee numeric(78,18) NOT NULL,
       gas_price numeric(78,18) NOT NULL,
       gas_limit numeric(78,0) NOT NULL,
       gas_used numeric(78,0) NOT NULL,
       input_data, varchar(128) NOT NULL
      )', 'block_data_' || node_name);
END
$func$;

SELECT create_table_transaction_data('eth');
SELECT create_table_transaction_data('etc');
SELECT create_table_transaction_data('bsc');


CREATE OR REPLACE FUNCTION create_table_internal_transaction_data(node_name varchar(3))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       unique_id PRIMARY KEY NOT NULL,
       block_hash varchar(256) NOT NULL
       transaction_hash varchar(256) NOT NULL ,
       block_number bigint,
       timestamp timestamp NOT NULL ,
       from_address varchar(256) NOT NULL ,
       to_address varchar(256) NOT NULL
       value bigint,
       gas_price bigint,
       gas_limit bigint NOT NULL,
       gas_used bigint NOT NULL,
       input_data varchar(128) NOT NULL,
       function_type,
      )', 'transaction_data_' || node_name);
END
$func$;

SELECT create_table_internal_transaction_data('eth');
SELECT create_table_internal_transaction_data('etc');
SELECT create_table_internal_transaction_data('bsc');



CREATE OR REPLACE FUNCTION create_table_transaction_logs_data(node_name varchar(3))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       unique_id PRIMARY KEY,
       transaction_hash varchar(256) NOT NULL,
       block_hash varchar(256) NOT NULL,
       block_number bigint,
       contract_Address varchar(256),
       from varchar(256) NOT NULL,
       to varchar(256) NOT NULL,
       gas_used bigint NOT NULL,
       logs_bloom varchar(256) NOT NULL,
      )', 'transaction_log_data_' || node_name);
END
$func$;


SELECT create_table_transaction_log_data('eth');
SELECT create_table_transaction_log_data('etc');
SELECT create_table_transaction_log_data('bsc');