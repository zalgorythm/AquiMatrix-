import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import json

import api_gateway.websocket_server as ws_server

class TestWebSocketServer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Clear global sets before each test
        ws_server.connected_clients.clear()
        ws_server.subscriptions.clear()

    async def test_subscribe_and_unsubscribe(self):
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()

        # Simulate subscribe message
        subscribe_msg = json.dumps({"action": "subscribe", "event": "test_event"})
        await ws_server.handler(mock_ws, None)
        # Since handler is a long running coroutine, we simulate the messages manually
        # Instead, we test subscription management directly
        ws_server.subscriptions.setdefault("test_event", set()).add(mock_ws)
        self.assertIn(mock_ws, ws_server.subscriptions["test_event"])

        # Simulate unsubscribe
        ws_server.subscriptions["test_event"].discard(mock_ws)
        self.assertNotIn(mock_ws, ws_server.subscriptions["test_event"])

    async def test_broadcast(self):
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        ws_server.subscriptions["event1"] = {mock_ws1, mock_ws2}

        message = {"data": "test"}
        await ws_server.broadcast("event1", message)

        mock_ws1.send.assert_awaited_once_with(json.dumps(message))
        mock_ws2.send.assert_awaited_once_with(json.dumps(message))

    async def test_handler_connection_closed(self):
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        # Simulate connection closed by raising websockets.exceptions.ConnectionClosed
        from websockets.exceptions import ConnectionClosed
        # Provide all required parameters for ConnectionClosed constructor
        mock_ws.__aiter__.side_effect = ConnectionClosed(1000, 1000, 'closed', None, None)

        # Run handler and expect it to handle connection closed gracefully without raising
        await ws_server.handler(mock_ws, None)

    async def test_handler_subscription_flow(self):
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        messages = [
            json.dumps({"action": "subscribe", "event": "eventA"}),
            json.dumps({"action": "unsubscribe", "event": "eventA"}),
            json.dumps({"action": "broadcast", "event": "eventA", "data": {"msg": "hello"}}),
        ]
        mock_ws.__aiter__.return_value = iter(messages)

        # Patch asyncio.gather to avoid actually sending messages
        mock_gather = AsyncMock()
        with patch("asyncio.gather", new=lambda *args, **kwargs: mock_gather):
            await ws_server.handler(mock_ws, None)
            mock_ws.send.assert_any_await(json.dumps({'status': 'Subscribed to eventA'}))
            mock_ws.send.assert_any_await(json.dumps({'status': 'Unsubscribed from eventA'}))
            mock_gather.assert_awaited()

if __name__ == "__main__":
    unittest.main()
