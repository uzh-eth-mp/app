import unittest
from . import get_events

class UNISWAP(unittest.IsolatedAsyncioTestCase):
    async def test_mint(self):
        self.maxDiff = None
        contract_address = "0xE6C78983b07a07e0523b57E18AA23d3Ae2519E05"
        tx_hash = ""

        events = set(await get_events(tx_hash, contract_address))

        expected_events = set()
        self.assertEqual(events, expected_events)

    async def test_burn(self):
        pass


