--- Uniswap: Swap entries in eth_transaction_logs not showing in eth_pair_liquidity_change

SELECT transaction_hash, address
FROM eth_transaction_logs T
WHERE 
  topics[1] LIKE '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'
  AND
  NOT EXISTS (
   SELECT 
   FROM   eth_pair_liquidity_change C
   WHERE  C.transaction_hash = T.transaction_hash AND C.address = T.address
   );

--- Uniswap: Swap entries in eth_pair_liquidity_change not showing in eth_transaction_logs

SELECT transaction_hash, address
FROM eth_pair_liquidity_change C
WHERE 
  NOT EXISTS (
   SELECT 
   FROM  eth_transaction_logs T
   WHERE  C.transaction_hash = T.transaction_hash AND C.address = T.address AND T.topics[1] LIKE '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'
   );

-- Uniswap: Mint entries in eth_transaction_logs
SELECT transaction_hash, address
FROM eth_transaction_logs T
WHERE topics[1] LIKE '0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f';


-- Uniswap: Burn entries in eth_transaction_logs
SELECT transaction_hash, address
FROM eth_transaction_logs T
WHERE topics[1] LIKE '0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496';