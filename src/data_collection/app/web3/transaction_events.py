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


def get_transaction_events(contract, receipt):
    # ABI for ERC20 https://gist.github.com/veox/8800debbf56e24718f9f483e1e40c35c

    burnAddresses = {"0x0000000000000000000000000000000000000000",
                   "0x000000000000000000000000000000000000dead"}

    #here, contract contains ABI, which has the definition of Transfer().
    #https://web3py.readthedocs.io/en/latest/contracts.html#web3.contract.ContractEvents.myEvent

    #there might be multiple emits in the contract, that's why we're looping, and use yield.
    for eventLog in contract.events.Transfer().processReceipt(receipt):
        if eventLog['event'] == "Transfer":
            src = eventLog['args']['from']
            dst = eventLog['args']['to']
            val = eventLog['args']['value']
            if dst in burnAddresses and src in burnAddresses:
                pass
            #https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol#L298
            if dst in burnAddresses:
                yield BurnEvent(src, val, receipt.contract_address)
            #https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol#L269
            elif src in burnAddresses:
                yield MintEvent(dst, val, receipt.contract_address)
            else:
                yield TransferEvent(src, dst, val, receipt.contract_address)
