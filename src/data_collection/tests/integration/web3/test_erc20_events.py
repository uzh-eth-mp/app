import unittest
from . import get_events

class ERC20(unittest.IsolatedAsyncioTestCase):
    async def test_mint(self):
        self.maxDiff = None
        contract_address = "0xc00e94Cb662C3520282E6f5717214004A7f26888"
        tx_hash = ""

        events = set(await get_events(tx_hash, contract_address))

        expected_events = set()
        self.assertEqual(events, expected_events)

    async def test_burn(self):
        pass


