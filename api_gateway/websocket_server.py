"""
websocket_server.py

Manages WebSocket connections for real-time updates.
Features:
1. Subscriptions: Clients subscribe to events via WebSocket handshake.
2. Event Broadcasting: Pushes updates to subscribed clients.
3. Persistence: Maintains connection state with timeouts.
Built with asyncio and websockets.
"""

import asyncio
import websockets
import json
import logging

connected_clients = set()
subscriptions = {}

logger = logging.getLogger('websocket_server')

async def handler(websocket, path=None):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get('action')
            if action == 'subscribe':
                event = data.get('event')
                if event:
                    subscriptions.setdefault(event, set()).add(websocket)
                    await websocket.send(json.dumps({'status': f'Subscribed to {event}'}))
            elif action == 'unsubscribe':
                event = data.get('event')
                if event and event in subscriptions:
                    subscriptions[event].discard(websocket)
                    await websocket.send(json.dumps({'status': f'Unsubscribed from {event}'}))
            elif action == 'broadcast':
                event = data.get('event')
                message_data = data.get('data')
                if event and message_data and event in subscriptions:
                    clients = subscriptions[event]
                    if clients:
                        await asyncio.gather(*(client.send(json.dumps(message_data)) for client in clients))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        for subs in subscriptions.values():
            subs.discard(websocket)

async def broadcast(event, message):
    if event in subscriptions:
        clients = subscriptions[event]
        if clients:
            await asyncio.wait([client.send(json.dumps(message)) for client in clients])

def start_server():
    return websockets.serve(handler, '0.0.0.0', 9001)

async def main():
    server = await start_server()
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
