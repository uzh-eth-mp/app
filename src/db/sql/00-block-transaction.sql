-- https://dba.stackexchange.com/a/42930

CREATE OR REPLACE FUNCTION create_table_block(node_name varchar(3))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       block_number bigint PRIMARY KEY NOT NULL,
       block_hash bytea NOT NULL,
       nonce bytea NOT NULL,
       difficulty numeric(78,0) NOT NULL,
       gas_limit bigint NOT NULL,
       gas_used bigint NOT NULL,
       timestamp timestamp NOT NULL,
       miner bytea NOT NULL,
       parent_hash bytea NOT NULL,
       static_block_reward numeric(78,18) NOT NULL,
       uncles bytea ARRAY

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
       transaction_hash bytea PRIMARY KEY NOT NULL,
       block_number bigint REFERENCES %I NOT NULL,
       from_address bytea NOT NULL,
       to_address bytea,
       value numeric(78,18),
       transaction_fee numeric(78,18) NOT NULL,
       gas_price numeric(78,18) NOT NULL,
       gas_limit numeric(78,0) NOT NULL,
       gas_used numeric(78,0) NOT NULL,
       is_token_tx boolean NOT NULL,
       input_data bytea NOT NULL
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
       transaction_hash bytea REFERENCES %I NOT NULL,
       from_address bytea NOT NULL ,
       to_address bytea NOT NULL,
       value numeric(78,18),
       gas_limit bigint NOT NULL,
       gas_used bigint,
       input_data bytea NOT NULL,
       call_type bytea NOT NULL,
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
       transaction_hash bytea REFERENCES %I NOT NULL,
       address bytea NOT NULL,
       log_index int,
       data bytea NOT NULL,
       removed boolean NOT NULL,
       topics bytea ARRAY,
       PRIMARY KEY (unique_id)
      )', node_name || '_transaction_logs' , node_name || '_transaction');
END
$func$;


SELECT create_table_transaction_logs('eth');
SELECT create_table_transaction_logs('etc');
SELECT create_table_transaction_logs('bsc');