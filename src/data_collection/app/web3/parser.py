import collections
from typing import (
    Any,
    Dict,
    List,
    Optional
)

from eth_hash.auto import keccak
from web3 import Web3
import collections, json

from app.model.abi import ERCABI
from app.model.contract import ContractCategory, ContractData

_contracts = json.load(open("etc/cfg/contracts.json"))
_contract_categories = collections.defaultdict(None)
for _ in _contracts:
    _contract_categories[_["address"].lower()] = ContractCategory(_["abi"])
def _get_contract_category(address):
    return _contract_categories[address.lower()]


class ContractParser:
    """Parse contract data"""

    def __init__(self, web3: Web3, erc_abi: ERCABI) -> None:
        self.w3 = web3
        self.erc_abi = erc_abi

    def _contract_has_function(self, code: str, fn_signature: str) -> bool:
        """
        Return `True` if the given code string contains
        the given function signature.
        """
        fn_hash = keccak(fn_signature.encode()).hex()
        fn_hash = f"63{fn_hash[:8]}"
        return fn_hash in code

    def _get_contract_category(self, code: str) -> Optional[ContractCategory]:
        """Determine the category of a contract from its code.

        Note:
            This method checks whether the contract code contains some functions.
            Depending on which functions it contains, it decides on the category.
            The predicates for different contract categories *should* be
            mutually exclusive.

        Returns:
            ContractCategory or None if the contract doesn't match any category
        """
        is_erc20 = \
            self._contract_has_function(code, "transfer(address,uint256)") and \
            self._contract_has_function(code, "transferFrom(address,address,uint256)")
        if is_erc20:
            return ContractCategory.ERC20
        is_erc721 = \
            not self._contract_has_function(code, "transfer(address,uint256)") and \
            self._contract_has_function(code, "transferFrom(address,address,uint256)")
        if is_erc721:
            return ContractCategory.ERC721
        is_erc1155 = self._contract_has_function(
            code,
            "safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)"
        )
        if is_erc1155:
            return ContractCategory.ERC1155

        # Return None if the contract category is unknown
        return None

    def _get_contract_abi(
        self, contract_category: ContractCategory
    ) -> Optional[List[Dict[str, Any]]]:
        """Return contract ABI depending on the contract category"""
        abi = None
        if contract_category == ContractCategory.ERC20:
            abi = self.erc_abi.erc20
        elif contract_category == ContractCategory.ERC721:
            abi = self.erc_abi.erc721
        elif contract_category == ContractCategory.ERC1155:
            abi = self.erc_abi.erc1155
        return abi

    async def get_contract_data(self, contract_address: str) -> Optional[ContractData]:
        """Obtain and parse data for a given contract address

        Returns:
            a ContractData instance
        """
        # Need to obtain contract category first
        #code = (await self.w3.eth.get_code(contract_address)).hex()
        #category = self._get_contract_category(code=code)
        category = _get_contract_category(contract_address)
        abi = self._get_contract_abi(contract_category=category)

        # Create a w3 contract instance
        contract = self.w3.eth.contract(
            address=contract_address,
            abi=abi
        )

        if category == ContractCategory.ERC20 or category == ContractCategory.ERC721:
            symbol = await contract.functions.symbol().call()
            name = await contract.functions.name().call()
            decimals = await contract.functions.decimals().call()
            total_supply = await contract.functions.totalSupply().call()
        elif category == ContractCategory.ERC1155:
            # FIXME: what should we do with ERC1155?
            # ERC1155 doesn't have any values
            symbol, name, decimals, total_supply = None, None, None, None
        else:
            # Return None if the contract has unknown category
            return None

        return ContractData(
            address=contract_address,
            code=code,
            symbol=symbol,
            name=name,
            decimals=decimals,
            total_supply=total_supply,
            token_category=category,
            w3_data=contract
        )
