import unittest
from . import get_events





class AAVE(unittest.IsolatedAsyncioTestCase):
    async def test_mint(self):
        self.maxDiff = None
        contract_address = "0x398eC7346DcD622eDc5ae82352F02bE94C62d119"
        tx_hash = ""

        events = set(await get_events(tx_hash, contract_address))

        expected_events = set()
        self.assertEqual(events, expected_events)

    async def test_burn(self):
        pass


