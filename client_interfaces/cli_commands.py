"""
Provides a command-line interface (CLI) for interacting with AquiMatrix.
Features:
1. Account Management: create-account generates keypairs.
2. Entry Submission: submit-entry crafts and sends entries to API.
3. State Queries: get-state fetches contract data.
4. Network Monitoring: status displays node stats.
Built with argparse.
"""

import argparse
import requests
import json
import sys
import subprocess
from consensus_engine.audit_report import generate_audit_report

API_URL = "http://localhost:9000"

from client_interfaces.cli_wallet import create_wallet, get_public_key_hex, sign_message

def create_account():
    create_wallet()

def submit_entry(entry_data):
    # Sign the entry data before submission
    import json
    from mining_backend import create_entry  # reuse create_entry to build entry dict

    # Load private key and sign entry
    # Prepare entry data for signing
    predecessor_hashes = entry_data.get("predecessor_hashes", [])
    nonce = entry_data.get("nonce", 0)

    # Create entry dict with real public key and signature
    public_key_hex = get_public_key_hex()
    # Create entry dict without signature and hash first
    entry = create_entry(predecessor_hashes, nonce)
    # Serialize entry for signing
    sign_data = json.dumps({
        "predecessor_hashes": predecessor_hashes,
        "timestamp": entry["timestamp"],
        "transaction_data": entry["transaction_data"],
        "submitter_public_key": public_key_hex,
    }, sort_keys=True).encode()

    signature_bytes = sign_message(sign_data)
    signature_hex = signature_bytes.hex()

    # Add real public key and signature to entry
    entry["submitter_public_key"] = public_key_hex
    entry["signature"] = signature_hex

    # Compute entry hash
    import hashlib
    entry_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    entry["hash"] = entry_hash

    # Submit entry to API
    import requests
    API_URL = "http://localhost:9000"
    response = requests.post(f"{API_URL}/entries", json=entry)
    if response.status_code == 200:
        print("Entry submitted successfully.")
    else:
        print(f"Failed to submit entry: {response.text}")

def submit_entry(entry_data):
    # This function is now replaced by the new submit_entry with signing
    pass

def get_state(address):
    response = requests.get(f"{API_URL}/state/{address}")
    if response.status_code == 200:
        print(f"State for {address}: {response.json()}")
    else:
        print(f"Failed to get state: {response.text}")

def status():
    # Placeholder for node status
    print("Node status: Running")

def get_dag_tips():
    try:
        response = requests.get(f"{API_URL}/dag/tips")
        if response.status_code == 200:
            print("DAG Tips:")
            for tip in response.json().get('tips', []):
                print(f" - {tip}")
        else:
            print(f"Failed to get DAG tips: {response.text}")
    except Exception as e:
        print(f"Error fetching DAG tips: {str(e)}")

def get_state_root():
    try:
        response = requests.get(f"{API_URL}/state/root")
        if response.status_code == 200:
            print(f"State Root: {response.json().get('state_root')}")
        else:
            print(f"Failed to get state root: {response.text}")
    except Exception as e:
        print(f"Error fetching state root: {str(e)}")

def audit_report():
    report = generate_audit_report()
    print(report)

def main():
    parser = argparse.ArgumentParser(description="AquiMatrix CLI")
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('create-account')
    submit_parser = subparsers.add_parser('submit-entry')
    submit_parser.add_argument('entry_file', help='Path to entry JSON file')

    get_state_parser = subparsers.add_parser('get-state')
    get_state_parser.add_argument('address', help='Contract address')

    subparsers.add_parser('status')

    subparsers.add_parser('get-dag-tips')
    subparsers.add_parser('get-state-root')

    # Add new subparser for mining-dashboard
    subparsers.add_parser('mining-dashboard')

    # Add new subparser for audit-report
    subparsers.add_parser('audit-report')

    # Add new subparser for LRW balance
    lrw_balance_parser = subparsers.add_parser('lrw-balance')
    lrw_balance_parser.add_argument('user_id', help='User ID to query LRW balance')

    # Add new subparser for LRW transfer
    lrw_transfer_parser = subparsers.add_parser('lrw-transfer')
    lrw_transfer_parser.add_argument('from_user', help='Sender user ID')
    lrw_transfer_parser.add_argument('to_user', help='Recipient user ID')
    lrw_transfer_parser.add_argument('amount', type=int, help='Amount of LRW to transfer')

    # Add new subparser for staking commands
    stake_parser = subparsers.add_parser('stake')
    stake_parser.add_argument('user_id', help='User ID to stake tokens')
    stake_parser.add_argument('amount', type=int, help='Amount of WŁC to stake')

    unstake_parser = subparsers.add_parser('unstake')
    unstake_parser.add_argument('user_id', help='User ID to unstake tokens')
    unstake_parser.add_argument('amount', type=int, help='Amount of WŁC to unstake')

    stake_balance_parser = subparsers.add_parser('stake-balance')
    stake_balance_parser.add_argument('user_id', help='User ID to query staked balance')

    claim_rewards_parser = subparsers.add_parser('claim-rewards')
    claim_rewards_parser.add_argument('user_id', help='User ID to claim staking rewards')

    args = parser.parse_args()

    if args.command == 'create-account':
        create_account()
    elif args.command == 'submit-entry':
        with open(args.entry_file) as f:
            entry_data = json.load(f)
        submit_entry(entry_data)
    elif args.command == 'get-state':
        get_state(args.address)
    elif args.command == 'status':
        status()
    elif args.command == 'get-dag-tips':
        get_dag_tips()
    elif args.command == 'get-state-root':
        get_state_root()
    elif args.command == 'mining-dashboard':
        # Run the mining_dashboard.py script
        subprocess.run([sys.executable, 'client_interfaces/mining_dashboard.py'])
    elif args.command == 'audit-report':
        audit_report()
    elif args.command == 'lrw-balance':
        balance = database_access.get_lrw_balance(db_instance, args.user_id)
        print(f"LRW balance for {args.user_id}: {balance}")
    elif args.command == 'lrw-transfer':
        from_balance = database_access.get_lrw_balance(db_instance, args.from_user)
        if from_balance < args.amount:
            print(f"Insufficient LRW balance for user {args.from_user}")
            return
        to_balance = database_access.get_lrw_balance(db_instance, args.to_user)
        database_access.store_lrw_balance(db_instance, args.from_user, from_balance - args.amount)
        database_access.store_lrw_balance(db_instance, args.to_user, to_balance + args.amount)
        print(f"Transferred {args.amount} LRW from {args.from_user} to {args.to_user}")
    elif args.command == 'stake':
        try:
            consensus_engine.token_rewards.stake_tokens(db_instance, args.user_id, args.amount)
            print(f"User {args.user_id} staked {args.amount} WŁC tokens.")
        except ValueError as e:
            print(str(e))
    elif args.command == 'unstake':
        try:
            consensus_engine.token_rewards.unstake_tokens(db_instance, args.user_id, args.amount)
            print(f"User {args.user_id} unstaked {args.amount} WŁC tokens.")
        except ValueError as e:
            print(str(e))
    elif args.command == 'stake-balance':
        balance = database_access.get_stake_balance(db_instance, args.user_id)
        print(f"Staked balance for {args.user_id}: {balance}")
    elif args.command == 'claim-rewards':
        rewards = database_access.get_staking_rewards(db_instance, args.user_id)
        if rewards > 0:
            current_balance = database_access.get_token_balance(db_instance, args.user_id)
            new_balance = current_balance + rewards
            database_access.store_token_balance(db_instance, args.user_id, new_balance)
            database_access.store_staking_rewards(db_instance, args.user_id, 0)
            print(f"User {args.user_id} claimed {rewards:.6f} WŁC staking rewards.")
        else:
            print(f"No staking rewards to claim for {args.user_id}.")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
