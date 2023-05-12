from enum import Enum
from multiprocessing.sharedctypes import Value
from typing import List

from hexbytes import HexBytes
from pydantic import BaseModel, root_validator, validator


def convert_string_to_bytes(cls,v): 
    return bytes(v)
    


class DataCollectionMode(Enum):
    """The mode of the application: producing or consuming data"""

    PRODUCER = "producer"
    CONSUMER = "consumer"


class Web3BaseModel(BaseModel):
    """Base class for any BaseModel related to web3 data"""

    @root_validator(allow_reuse=True, pre=True)
    def transform_hexbytes(cls, values):
        """Transforms every HexBytes instance into a string value.

        Note:
            Any HexBytes value should be implicitly typed as 'str' in the pydantic model
            inheriting from this class.
        """
        for key, value in values.items():
            if isinstance(value, HexBytes):
                values[key] = value.hex()
            elif isinstance(value, List):
                # If the value is a list, recursively transform
                # potential hexbytes values
                values[key] = list(
                    map(lambda v: v.hex() if isinstance(v, HexBytes) else v, value)
                )
        return values

