from app.model.contract import ContractCategory

class ContractEvent:
    """
    Contract events are the emitted events by the contract included in the transaction receipt (output of the
    interaction with a smart contract).
    """
    pass

class MintEvent(ContractEvent):
    """
    This represents mint event.
    """
    def __init__(self, contract_address, account, value):
        self.contract_address = contract_address
        self.account = account
        self.value = value

class BurnEvent(ContractEvent):
    """
    This represents burn event.
    """
    def __init__(self, contract_address, account, value):
        self.contract_address = contract_address
        self.account = account
        self.value = value


class TransferEvent(ContractEvent):
    """
    This represents transfer event between two addreses.
    """
    def __init__(self, contract_address, src, dst, value):
        self.contract_address = contract_address
        self.src = src
        self.dst = dst
        self.value = value

def _get_erc20_transaction_events(contract, receipt, block_hash):
    # ABI for ERC20 https://gist.github.com/veox/8800debbf56e24718f9f483e1e40c35c

    burnAddresses = {"0x0000000000000000000000000000000000000000",
                     "0x000000000000000000000000000000000000dead"}

    # here, contract contains ABI, which has the definition of Transfer().
    # https://web3py.readthedocs.io/en/latest/contracts.html#web3.contract.ContractEvents.myEvent

    # there might be multiple emits in the contract, that's why we're looping, and use yield.
    for eventLog in contract.events.Transfer().processReceipt(receipt):
        if eventLog['event'] == "Transfer":
            src = eventLog['args']['from']
            dst = eventLog['args']['to']
            val = eventLog['args']['value']
            if dst in burnAddresses and src in burnAddresses:
                pass
            # https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol#L298
            if dst in burnAddresses:
                yield BurnEvent(src, val, receipt.contract_address)
            # https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol#L269
            elif src in burnAddresses:
                yield MintEvent(dst, val, receipt.contract_address)
            else:
                yield TransferEvent(src, dst, val, receipt.contract_address)
    #USDT - https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code#L444
    # Redeem = USDT owner creates tokens.
    for eventLog in contract.events.Issue().processReceipt(receipt):
        val = eventLog['args']['amount']
        yield MintEvent(contract.functions.getOwner().call(block_identifier=block_hash), val, receipt.contract_address)
    #Redeem = USDT owner makes tokens dissapear - no null address. if they transfer to null address, still burn.
    #getOwner -> https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code#L275
    # TODO how to get the owner account a given point in time? Owner can change at any time.
    for eventLog in contract.events.Redeem().processReceipt(receipt):
        val = eventLog['args']['amount']
        yield BurnEvent(contract.functions.getOwner().call(block_identifier=block_hash), val, receipt.contract_address)

def _get_uniSwapV2_transaction_events(contract, receipt, block_hash):
    for eventLog in contract.events.PairCreated().processReceipt(receipt):
        token0 = eventLog['args']['token0']
        token1 = eventLog['args']['token1']
        pair = eventLog['args']['pair']
        value = eventLog['args']['']
    return

def get_transaction_events(contract, receipt, block_hash):
    if contract.category == ContractCategory.ERC20:
        return _get_erc20_transaction_events(contract, receipt, block_hash)
    if contract.category == ContractCategory.UNI_SWAP_V2:
        return _get_uniSwapV2_transaction_events(contract, receipt, block_hash)
    return
