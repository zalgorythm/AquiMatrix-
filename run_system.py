import asyncio
import logging
from network.p2p_network import P2PNetwork
import mining_backend

logging.basicConfig(level=logging.INFO)

async def main():
    p2p = P2PNetwork()
    await p2p.start_server()
    mining_task = asyncio.create_task(mining_backend.mining_real())
    try:
        await mining_task
    except asyncio.CancelledError:
        pass
    finally:
        await p2p.stop_server()

if __name__ == "__main__":
    asyncio.run(main())
