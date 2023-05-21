import unittest
from . import get_events


class USDT(unittest.IsolatedAsyncioTestCase):
    async def test_mint(self):
        self.maxDiff = None
        contract_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        tx_hash = ""

        events = set(await get_events(tx_hash, contract_address))

        expected_events = set()
        self.assertEqual(events, expected_events)

    async def test_burn(self):
        pass


