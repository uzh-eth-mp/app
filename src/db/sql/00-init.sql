-- https://dba.stackexchange.com/a/42930

CREATE OR REPLACE FUNCTION create_table_block_data(node_name varchar(3))
  RETURNS VOID
  LANGUAGE plpgsql AS
$func$
BEGIN
   EXECUTE format('
      CREATE TABLE IF NOT EXISTS %I (
       number serial PRIMARY KEY,
       hash varchar(128),
       difficulty varchar(256),
       gas_limit varchar(256)
      )', 'block_data_' || node_name);
END
$func$;

SELECT create_table_block_data('eth');
SELECT create_table_block_data('etc');
SELECT create_table_block_data('bsc');
