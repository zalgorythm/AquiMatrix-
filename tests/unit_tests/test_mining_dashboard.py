import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
import sys
import io
import json

from client_interfaces.mining_dashboard import MiningDashboard
from client_interfaces.malformed_json_parser import parse_malformed_json

class TestMiningDashboard(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.dashboard = MiningDashboard()

    def test_initial_status(self):
        self.assertEqual(self.dashboard.status["status"], "UNKNOWN")
        self.assertEqual(self.dashboard.status["nonce"], 0)

    def test_parse_malformed_json_integration(self):
        malformed_msg = '{"status":"MINING" "nonce":123 "hashrate":456}'
        parsed = parse_malformed_json(malformed_msg)
        self.assertIsInstance(parsed, dict)
        self.assertEqual(parsed.get("status"), "MINING")
        self.assertEqual(parsed.get("nonce"), 123)
        self.assertEqual(parsed.get("hashrate"), 456)

    def test_status_update(self):
        update = {"status": "MINING", "nonce": 10}
        self.dashboard.status.update(update)
        self.assertEqual(self.dashboard.status["status"], "MINING")
        self.assertEqual(self.dashboard.status["nonce"], 10)

    def test_render_output(self):
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.dashboard.render()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("MINING DASHBOARD", output)
        self.assertIn("Status:", output)

    @patch("client_interfaces.mining_dashboard.websockets.connect", new_callable=AsyncMock)
    async def test_connect_success(self, mock_connect):
        mock_websocket = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_websocket
        mock_websocket.recv = AsyncMock(side_effect=[
            json.dumps({"status": "MINING"}),
            asyncio.CancelledError()
        ])
        self.dashboard.should_exit = False
        with patch.object(self.dashboard, "render") as mock_render:
            with self.assertRaises(asyncio.CancelledError):
                await self.dashboard.connect()
            mock_render.assert_called()

    @patch("client_interfaces.mining_dashboard.websockets.connect", new_callable=AsyncMock)
    async def test_connect_retry(self, mock_connect):
        mock_connect.side_effect = ConnectionRefusedError()
        self.dashboard.max_retries = 2
        self.dashboard.retry_count = 0
        with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
            await self.dashboard.connect()
            self.assertEqual(self.dashboard.retry_count, 2)
            mock_sleep.assert_called()

    def test_stop(self):
        self.dashboard.stop()
        self.assertTrue(self.dashboard.should_exit)

if __name__ == "__main__":
    unittest.main()
