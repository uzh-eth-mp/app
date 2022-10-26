# Flow of event extraction

1. Get transactions from block
2. Get receipt from transaction
3. Get contract from receipt
4. Get ABI from contract address from [contracts.json](../../../etc/cfg/contracts.json)
5. Load contract at the given block (it might change due to proxying) & get events from receipt.
6. Map each event to our event representation according to **Event mapping**.

# Event representation
We extract the following events from tracked contracts. Events are defined in this [file](../transaction_events.py).
## TransferEvent
``
Transfer(from, to, amount)
``

## BurnEvent

## MintEvent

## PairCreatedEvent


# Event mapping
For contracts with ABI defined as ERC20 in [abi.json](../../../etc/abi.json):
## Generic ERC20 contracts
Most ERC20 contracts repre

## USDT
USDT uses custom events Issue and Redeem to represent Minting and Burning. They transfer funds to a programmable address in the contract [called owner](link to usdt contract line defining owner) so the recipient of the minted coins might change over time.

## Uniswap
https://docs.uniswap.org/whitepaper.pdf
Uniswap factory things new contracts to look at, bla bla.
Most significantly, it enables the creation of arbitrary ERC20/ERC20
pairs, rather than supporting only pairs between ERC20 and ETH. It also provides a hard-
ened price oracle that accumulates the relative price of the two assets at the beginning of
each block. This allows other contracts on Ethereum to estimate the time-weighted average
price for the two assets over arbitrary intervals. Finally, it enables “flash swaps” where users
can receive assets freely and use them elsewhere on the chain, only paying for (or returning)
those assets at the end of the transaction.

# Lessons learned
- ERC20 is a standard smart contract interface, which were implemented by fungible tokens built on Ethereum. It specifies what contracts should be able to and only has the [functions](https://ethereum.org/en/developers/tutorials/transfers-and-approval-of-erc-20-tokens-from-a-solidity-smart-contract/) that can change the total supply:
  - Transfer
  - Approve 
- ERC721
- Actual implementations do whatever the fuck they want. For example:
  - some use transfer to/from account 0 to represent burning/minting. 
  - Others have their own custom events for these cases

- Proxy contracts 
  - Some contracts are implemented through proxies. This implies that the contract can change at any time, including which events are emitted as well as their correctness. For example, when [this contract was hacked](http://sth), wrong events were emitted. 


# Decisions made
- _Generic_ solutions for ERC20 will not work, and we have to read & validate every contract we want to track or accept that some data will be wrong.
  - We will keep a list of supported contracts, whose code we have read & validated. That list can be found in [this file](../../../etc/cfg/contracts.json).
 