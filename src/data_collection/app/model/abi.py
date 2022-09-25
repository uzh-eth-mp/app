from typing import Any, Dict, List

from pydantic import BaseModel


class ERCABI(BaseModel):
    """Model for ERC ABIs"""
    erc20: List[Dict[str, Any]]
    erc721: List[Dict[str, Any]]
    erc1155: List[Dict[str, Any]]
