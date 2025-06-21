import asyncio
import logging
import websockets
import json
import time
import hashlib
import requests
import lib.database_access as db_access
from network import p2p_network

logger = logging.getLogger('mining_backend')

API_URL = "http://localhost:9000"

def reset_ledger():
    # Clear the in-memory database to reset ledger state
    global db_access
    db_access.db_instance.entries.clear()
    db_access.db_instance.invalid_entries.clear()
    db_access.db_instance.token_balances.clear()
    db_access.db_instance.difficulties.clear()
    db_access.db_instance.timestamps.clear()
    logger.info("Ledger state has been reset to genesis.")

def create_entry(predecessor_hashes, nonce):
    timestamp = int(time.time())
    transaction_data = {
        "nonce": nonce,
        "data": "Sample transaction data"
    }
    submitter_public_key = "sample_public_key"  # Replace with actual key management
    # Construct entry dict without signature and hash first
    entry = {
        "predecessor_hashes": predecessor_hashes,
        "timestamp": timestamp,
        "transaction_data": transaction_data,
        "submitter_public_key": submitter_public_key,
    }
    # Create a string to sign (simplified)
    sign_data = json.dumps({
        "predecessor_hashes": predecessor_hashes,
        "timestamp": timestamp,
        "transaction_data": transaction_data,
        "submitter_public_key": submitter_public_key,
    }, sort_keys=True)
    # Dummy signature (replace with real signing)
    signature = hashlib.sha256(sign_data.encode()).hexdigest()
    entry["signature"] = signature
    # Compute entry hash
    entry_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    entry["hash"] = entry_hash
    return entry

async def send_mining_status(websocket):
    import random
    nonce = 0
    hash_count = 0
    start_time = time.time()
    hashrate = 0

    while True:
        current_time = time.time()
        elapsed = current_time - start_time

        # Calculate hashrate as hashes per second over last interval
        if elapsed >= 5:
            # Simulate varying hashrate for demonstration
            hashrate = random.randint(150, 250)
            start_time = current_time
            hash_count = 0

        # Increment hash count for this iteration (simulate hashes done)
        hash_count += 1000  # This should be replaced with real hash count if available

        # Fetch balance from ledger database if available
        balance = 0.0
        today_mining = 0.0
        pending_rewards = 0.0
        fees_paid = 0.0
        try:
            token_balances = db_access.db_instance.token_balances
            balance = token_balances.get("main_account", 0.0)
            # For demonstration, set other values statically or calculate as needed
            today_mining = balance * 0.05
            pending_rewards = balance * 0.025
            fees_paid = balance * 0.001
        except Exception as e:
            logger.error(f"Error fetching balance info: {e}")

        status = {
            "status": "Mining",
            "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            "nonce": nonce,
            "time": time.strftime("%H:%M:%S"),
            "hashrate": int(hashrate),
            "pof_stage_1": 50,
            "pof_stage_2": 75,
            "confirmation_levels": {
                "L0": 10,
                "L1": 5,
                "L2": 2,
                "L3": 1
            },
            "balance": balance,
            "today_mining": today_mining,
            "pending_rewards": pending_rewards,
            "fees_paid": fees_paid,
            "ledger_updated": True
        }
        import collections.abc

import collections.abc

def to_standard_dict(obj):
    if isinstance(obj, collections.abc.Mapping):
        return {str(k): to_standard_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_standard_dict(i) for i in obj]
    else:
        return obj

        standard_status = to_standard_dict(status)
        message = {
            "action": "broadcast",
            "event": "mining_status",
            "data": standard_status
        }
        standard_message = to_standard_dict(message)
        try:
            await websocket.send(json.dumps(standard_message))
            logger.info(f"Sent mining status update: nonce={nonce}, ledger_updated=True, hashrate={int(hashrate)}")
        except Exception as e:
            logger.error(f"Error sending mining status: {e}")
            break
        nonce += 1
        await asyncio.sleep(5)

async def mining_real():
    reset_ledger()
    uri = "ws://localhost:9001"
    nonce = 0
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Connected to WebSocket server for mining status updates.")
                # Start mining status broadcast in background
                asyncio.create_task(send_mining_status(websocket))
                while True:
                    # Get current tips from REST API
                    try:
                        response = requests.get(f"{API_URL}/dag/tips")
                        response.raise_for_status()
                        tips = response.json().get("tips", [])
                        if len(tips) < 3:
                            logger.warning("Less than 3 tips available, waiting...")
                            await asyncio.sleep(5)
                            continue
                        # Select 3 tips as predecessors
                        predecessors = tips[:3]
                        # Create new entry referencing these predecessors
                        entry = create_entry(predecessors, nonce)
                        # Submit entry to REST API
                        submit_resp = requests.post(f"{API_URL}/entries", json=entry)
                        if submit_resp.status_code == 200:
                            logger.info(f"Submitted entry with nonce {nonce} and hash {entry['hash']}")
                            # Propagate entry to peers via P2P network
                            try:
                                message = json.dumps({
                                    'type': 'entry_propagation',
                                    'entry': entry
                                })
                                # Broadcast to all connected peers
                                if hasattr(p2p_network, 'p2p_instance'):
                                    asyncio.create_task(p2p_network.p2p_instance.broadcast(message))
                            except Exception as e:
                                logger.error(f"Error propagating entry to peers: {e}")
                            nonce += 1
                        else:
                            logger.error(f"Failed to submit entry: {submit_resp.text}")
                    except Exception as e:
                        logger.error(f"Error during entry submission: {e}")
                    await asyncio.sleep(10)  # Wait before next mining attempt
        except Exception as e:
            logger.error(f"Connection error: {e}")
            logger.info("Retrying connection in 5 seconds...")
            await asyncio.sleep(5)

async def main():
    await mining_real()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
