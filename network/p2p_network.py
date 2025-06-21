"""
Basic peer-to-peer networking module for AquiMatrix.

Features:
- Peer connection management
- Entry propagation to peers
- State synchronization requests and responses
- Simple message broadcasting
"""

import asyncio
import websockets
import json
import logging

logger = logging.getLogger('p2p_network')

class P2PNetwork:
    def __init__(self, host='0.0.0.0', port=9002):
        self.host = host
        self.port = port
        self.peers = set()
        self.server = None

    async def handler(self, websocket, path):
        self.peers.add(websocket)
        logger.info(f"Peer connected: {websocket.remote_address}")
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Peer disconnected: {websocket.remote_address}")
        finally:
            self.peers.discard(websocket)

    async def process_message(self, websocket, message):
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            if msg_type == 'entry_propagation':
                entry = data.get('entry')
                logger.info(f"Received entry propagation from {websocket.remote_address}")
                # Validate and add entry to ledger
                from data_ingestion.entry_validator import EntryValidator
                from consensus_engine.dag_structure import DAG
                import lib.database_access as db_access

                validator = EntryValidator(db_access.db_instance)
                dag = DAG(db_access.db_instance)

                entry_hash = entry.get('hash')
                valid, msg = validator.validate_entry(entry, entry_hash)
                if valid:
                    try:
                        dag.add_entry(entry)
                        logger.info(f"Entry {entry_hash} added to DAG from peer propagation")
                        # Broadcast to other peers except sender
                        await self.broadcast(message, exclude=websocket)
                    except Exception as e:
                        logger.error(f"Failed to add entry to DAG: {e}")
                else:
                    logger.warning(f"Invalid entry received from peer: {msg}")
            elif msg_type == 'state_sync_request':
                logger.info(f"Received state sync request from {websocket.remote_address}")
                # Placeholder: respond with current ledger tips
                from consensus_engine.dag_structure import DAG
                import lib.database_access as db_access
                dag = DAG(db_access.db_instance)
                tips = dag.get_tips()
                response = json.dumps({
                    'type': 'state_sync_response',
                    'tips': tips
                })
                await websocket.send(response)
            elif msg_type == 'state_sync_response':
                logger.info(f"Received state sync response from {websocket.remote_address}")
                # Placeholder: process received tips (could request missing entries)
                # For now, just log
                tips = data.get('tips', [])
                logger.info(f"Peer tips: {tips}")
            else:
                logger.warning(f"Unknown message type: {msg_type}")
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")

    async def broadcast(self, message, exclude=None):
        if self.peers:
            await asyncio.wait([peer.send(message) for peer in self.peers if peer != exclude])

    async def start_server(self):
        self.server = await websockets.serve(self.handler, self.host, self.port)
        logger.info(f"P2P server started on {self.host}:{self.port}")

    async def stop_server(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("P2P server stopped")

async def main():
    p2p = P2PNetwork()
    await p2p.start_server()
    await asyncio.Future()  # run forever

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
