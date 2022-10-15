from app.model.contract import ContractCategory

class ContractEvent:
    """
    Contract events are the emitted events by the contract included in the transaction receipt (output of the
    interaction with a smart contract).
    """
    def __init__(self, contract_address):
        self.contract_address = contract_address

class MintFungibleEvent(ContractEvent):
    """
    This represents mint event.
    """
    def __init__(self, contract_address, account, value):
        super(contract_address)
        self.account = account
        self.value = value

class BurnFungibleEvent(ContractEvent):
    """
    This represents burn event.
    """
    def __init__(self, contract_address, account, value):
        super(contract_address)
        self.account = account
        self.value = value


class TransferFungibleEvent(ContractEvent):
    """
    This represents transfer event between two addreses.
    """
    def __init__(self, contract_address, src, dst, value):
        super(contract_address)
        self.src = src
        self.dst = dst
        self.value = value

class PairCreatedEvent(ContractEvent):
    """
    This represents the creation a contract for trading the token pair.
    """
    def __init__(self, factory_address, contract_address, token0, token1):
        super(contract_address)
        self.factory_address = factory_address
        self.token0 = token0
        self.token1 = token1

# https://ethereum.org/en/developers/tutorials/uniswap-v2-annotated-code/#pair-events
class MintPairEvent(ContractEvent):
    def __init__(self, contract_address, sender, amount0, amount1):
        super(contract_address)
        self.sender = sender
        self.amount0 = amount0
        self.amount1 = amount1
class BurnPairEvent(ContractEvent):
    def __init__(self, contract_address, src, dst, amount0, amount1):
        super(contract_address)
        self.src = src
        self.dst = dst
        self.amount0 = amount0
        self.amount1 = amount1
class SwapPairEvent(ContractEvent):
    def __init__(self, contract_address, src, dst, in0, in1, out0, out1):
        super(contract_address)
        self.src = src
        self.dst = dst
        self.in0 = in0
        self.in1 = in1
        self.out0 = out0
        self.out1 = out1

class MintNonFungibleEvent(ContractEvent):
    """
    This represents mint event.
    """
    def __init__(self, contract_address, account, tokenId):
        super(contract_address)
        self.account = account
        self.tokenId = tokenId

class BurnNonFungibleEvent(ContractEvent):
    """
    This represents burn event.
    """
    def __init__(self, contract_address, account, tokenId):
        super(contract_address)
        self.account = account
        self.tokenId = tokenId

class TransferNonFungibleEvent(ContractEvent):
    """
    This represents transfer event between two addresses.
    """
    def __init__(self, contract_address, src, dst, tokenId):
        super(contract_address)
        self.src = src
        self.dst = dst
        self.tokenId = tokenId

def _get_erc20_transaction_events(contract, receipt, block_hash):
    # ABI for ERC20 https://gist.github.com/veox/8800debbf56e24718f9f483e1e40c35c

    burnAddresses = {'0x0000000000000000000000000000000000000000',
                     '0x000000000000000000000000000000000000dead'}

    # here, contract contains ABI, which has the definition of Transfer().
    # https://web3py.readthedocs.io/en/latest/contracts.html#web3.contract.ContractEvents.myEvent

    # there might be multiple emits in the contract, that's why we're looping, and use yield.
    for eventLog in contract.events.Transfer().processReceipt(receipt):
        if eventLog['event'] == 'Transfer':
            src = eventLog['args']['from']
            dst = eventLog['args']['to']
            val = eventLog['args']['value']
            if dst in burnAddresses and src in burnAddresses:
                pass
            # https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol#L298
            if dst in burnAddresses:
                yield BurnFungibleEvent(receipt.contract_address, src, val)
            # https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol#L269
            elif src in burnAddresses:
                yield MintFungibleEvent(receipt.contract_address, dst, val)
            else:
                yield TransferFungibleEvent(receipt.contract_address, src, dst, val)
    #USDT -> https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code#L444
    # Redeem = USDT owner creates tokens.
    for eventLog in contract.events.Issue().processReceipt(receipt):
        val = eventLog['args']['amount']
        yield MintFungibleEvent(receipt.contract_address, contract.functions.getOwner().call(block_identifier=block_hash), val)
    #Redeem = USDT owner makes tokens dissapear - no null address. if they transfer to null address, still burn.
    #getOwner -> https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code#L275
    # TODO how to get the owner account a given point in time? Owner can change at any time.
    for eventLog in contract.events.Redeem().processReceipt(receipt):
        val = eventLog['args']['amount']
        yield BurnFungibleEvent(receipt.contract_address, contract.functions.getOwner().call(block_identifier=block_hash), val)

def _get_erc721_transaction_events(contract, receipt, block_hash):
    burnAddresses = {'0x0000000000000000000000000000000000000000',
                     '0x000000000000000000000000000000000000dead'}

    for eventLog in contract.events.Transfer().processReceipt(receipt):
        if eventLog['event'] == 'Transfer':
            src = eventLog['args']['from']
            dst = eventLog['args']['to']
            tokenId = eventLog['args']['tokenId']
            if dst in burnAddresses and src in burnAddresses:
                pass
            if dst in burnAddresses:
                yield BurnNonFungibleEvent(receipt.contract_address, src, tokenId)
            elif src in burnAddresses:
                yield MintNonFungibleEvent(receipt.contract_address, dst, tokenId)
            else:
                yield TransferNonFungibleEvent(receipt.contract_address, src, dst, tokenId)

# PairCreation -> https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Factory.sol#L13
def _get_uniSwapV2_factory_transaction_events(contract, receipt, block_hash):
    for eventLog in contract.events.PairCreated().processReceipt(receipt):
        token0 = eventLog['args']['token0']
        token1 = eventLog['args']['token1']
        pair = eventLog['args']['pair']
        yield PairCreatedEvent(receipt.contract_address, pair, token0, token1)

def _get_uniSwapV2_pair_transaction_events(contract, receipt, block_hash):
    for eventLog in contract.events.Mint().processReceipt(receipt):
        sender = eventLog['args']['sender']
        amount0 = eventLog['args']['amount0']
        amount1 = eventLog['args']['amount1']
        yield MintPairEvent(receipt.contract_address, sender, amount0, amount1)
    #https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol#L134
    # Burn of pairs in Uniswap -> taking back liquidity from the pool "to" their address or another one.
    for eventLog in contract.events.Burn().processReceipt(receipt):
        sender = eventLog['args']['sender']
        amount0 = eventLog['args']['amount0']
        amount1 = eventLog['args']['amount1']
        to = eventLog['args']['to']
        yield BurnPairEvent(receipt.contract_address, sender, to, amount0, amount1)
    for eventLog in contract.events.Swap().processReceipt(receipt):
        sender = eventLog['args']['sender']
        amount0In = eventLog['args']['amount0In']
        amount1In = eventLog['args']['amount1In']
        amount0Out = eventLog['args']['amount0Out']
        amount1Out = eventLog['args']['amount1Out']
        to = eventLog['args']['to']
        yield SwapPairEvent(sender, to, amount0In, amount1In, amount0Out, amount1Out)


def get_transaction_events(contract, receipt, block_hash):
    if contract.category == ContractCategory.ERC20:
        return _get_erc20_transaction_events(contract, receipt, block_hash)
    if contract.category == ContractCategory.ERC721:
        return _get_erc721_transaction_events(contract, receipt, block_hash)
    if contract.category == ContractCategory.UNI_SWAP_V2_FACTORY:
        return _get_uniSwapV2_factory_transaction_events(contract, receipt, block_hash)
    if contract.category == ContractCategory.UNI_SWAP_V2_PAIR:
        return _get_uniSwapV2_pair_transaction_events(contract, receipt, block_hash)
