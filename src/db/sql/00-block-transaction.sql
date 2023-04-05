-- https://dba.stackexchange.com/a/42930

CREATE OR REPLACE FUNCTION create_table_block(node_name varchar(3))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       block_number bigint PRIMARY KEY NOT NULL,
       block_hash varchar(256) NOT NULL,
       nonce varchar(256) NOT NULL,
       difficulty numeric(78,0) NOT NULL,
       gas_limit bigint NOT NULL,
       gas_used bigint NOT NULL,
       timestamp timestamp NOT NULL,
       miner varchar(256) NOT NULL,
       parent_hash varchar(256) NOT NULL,
       block_reward numeric(78,18) NOT NULL
      )', node_name || '_block') ;
END
$func$;

SELECT create_table_block('eth');
SELECT create_table_block('etc');
SELECT create_table_block('bsc');


CREATE OR REPLACE FUNCTION create_table_transaction(node_name varchar(3))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       transaction_hash varchar(256) PRIMARY KEY NOT NULL,
       block_number bigint REFERENCES %I NOT NULL,
       from_address varchar(256) NOT NULL,
       to_address varchar(256),
       value numeric(78,18),
       transaction_fee numeric(78,18) NOT NULL,
       gas_price numeric(78,18) NOT NULL,
       gas_limit numeric(78,0) NOT NULL,
       gas_used numeric(78,0) NOT NULL,
       is_token_tx boolean NOT NULL,
       input_data varchar(65536) NOT NULL
      )', node_name || '_transaction', node_name || '_block');
END
$func$;

SELECT create_table_transaction('eth');
SELECT create_table_transaction('etc');
SELECT create_table_transaction('bsc');


CREATE OR REPLACE FUNCTION create_table_internal_transaction(node_name varchar(3))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       unique_id UUID DEFAULT gen_random_uuid (),
       transaction_hash varchar(256) REFERENCES %I NOT NULL,
       from_address varchar(256) NOT NULL ,
       to_address varchar(256) NOT NULL,
       value numeric(78,18),
       gas_limit bigint NOT NULL,
       gas_used bigint,
       input_data varchar(256) NOT NULL,
       call_type varchar(256) NOT NULL,
       PRIMARY KEY (unique_id)
      )', node_name || '_internal_transaction', node_name || '_transaction');
END
$func$;

SELECT create_table_internal_transaction('eth');
SELECT create_table_internal_transaction('etc');
SELECT create_table_internal_transaction('bsc');


CREATE OR REPLACE FUNCTION create_table_transaction_logs(node_name varchar(3))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       unique_id UUID DEFAULT gen_random_uuid (),
       transaction_hash varchar(256) REFERENCES %I NOT NULL,
       address varchar(256) NOT NULL,
       log_index int,
       data varchar(256) NOT NULL,
       removed boolean NOT NULL,
       topics varchar(256) ARRAY,
       PRIMARY KEY (unique_id)
      )', node_name || '_transaction_logs' , node_name || '_transaction');
END
$func$;


SELECT create_table_transaction_logs('eth');
SELECT create_table_transaction_logs('etc');
SELECT create_table_transaction_logs('bsc');