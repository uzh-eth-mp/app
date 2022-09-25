from enum import Enum
from typing import List

from hexbytes import HexBytes
from pydantic import (
    BaseModel,
    root_validator
)


class DataCollectionMode(Enum):
    """The mode of the application: producing or consuming data"""
    PRODUCER = "producer"
    CONSUMER = "consumer"


class Web3BaseModel(BaseModel):
    """Base class for any BaseModel related to web3 data"""

    @root_validator(allow_reuse=True, pre=True)
    def transform_hexbytes(cls, values):
        """Transforms every HexBytes instance into a string value"""
        for key, value in values.items():
            if isinstance(value, HexBytes):
                values[key] = value.hex()
            elif isinstance(value, List):
                # If the value is a list, recursively transform
                # potential hexbytes values
                values[key] = list(
                    map(
                        lambda v: v.hex() if isinstance(v, HexBytes) else v,
                        value
                    )
                )
        return values
