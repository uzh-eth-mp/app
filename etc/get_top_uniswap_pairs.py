import requests
import json


# function to use requests.post to make an API call to the subgraph url
def run_query(query):
    # endpoint where you are making the request
    request = requests.post(
        "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2" "",
        json={"query": query},
    )
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed. return code is {}.      {}".format(
                request.status_code, query
            )
        )


query_init = """
{
 pairs(first: 100, orderBy: reserveUSD, orderDirection: desc) {
   id
   token0{
    id
    symbol
    name
    txCount
    totalLiquidity
    decimals
  }
   token1{
    id
    symbol
    name
    txCount
    totalLiquidity
    decimals
  }
   reserve0
   reserve1
   totalSupply
   reserveUSD
   reserveETH
   txCount
   createdAtTimestamp
   createdAtBlockNumber
 }
}
"""
query_result = run_query(query_init)

# Create the result json that will be used in our config
result = []
for pair in query_result["data"]["pairs"]:
    token0 = pair["token0"]
    token1 = pair["token1"]
    result.append(
        dict(
            address=pair["id"],
            symbol=f"UniSwap V2 Pair {token0['symbol']}-{token1['symbol']}",
            category="UniSwapV2Pair",
        )
    )

print(json.dumps(result, indent=2))
