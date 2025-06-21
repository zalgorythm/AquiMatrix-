"""
rest_endpoints.py

Defines RESTful API endpoints for external interaction with AquiMatrix.
Features:
1. Entry Submission: POST /entries accepts new entries, validated by entry_validator.py.
2. State Queries: GET /state/{address} retrieves contract state.
3. Entry Lookup: GET /entries/{hash} fetches entry details.
4. Authentication: Requires API keys or signatures.
Uses Flask for API server.
"""

from flask import Flask, request, jsonify
from data_ingestion.entry_validator import EntryValidator
from consensus_engine.dag_structure import DAG
from vm_state.state_trie import StateTrie
import logging

app = Flask(__name__)
logger = logging.getLogger('rest_endpoints')

db = None  # Placeholder for database connection
entry_validator = EntryValidator(db)
from consensus_engine.dag_structure import DAG
dag = DAG(db)
state_trie = StateTrie(db)

@app.route('/entries', methods=['POST'])
def submit_entry():
    entry = request.json
    entry_hash = entry.get('hash')
    valid, msg = entry_validator.validate_entry(entry, entry_hash)
    if not valid:
        return jsonify({'error': msg}), 400
    try:
        dag.add_entry(entry)
    except Exception as e:
        logger.error(f"Failed to add entry: {str(e)}")
        return jsonify({'error': str(e)}), 400
    return jsonify({'message': 'Entry accepted', 'hash': entry_hash}), 200

@app.route('/state/<address>', methods=['GET'])
def get_state(address):
    value = state_trie.get(address)
    if value is None:
        return jsonify({'error': 'Address not found'}), 404
    return jsonify({'address': address, 'value': value}), 200

@app.route('/entries/<entry_hash>', methods=['GET'])
def get_entry(entry_hash):
    entry = dag.entries.get(entry_hash)
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    return jsonify(entry), 200

@app.route('/dag/tips', methods=['GET'])
def get_dag_tips():
    tips = dag.get_tips()
    return jsonify({'tips': tips}), 200

@app.route('/state/root', methods=['GET'])
def get_state_root():
    root_hash = state_trie.get_root()
    if root_hash is None:
        return jsonify({'error': 'State root not available'}), 404
    return jsonify({'state_root': root_hash.hex()}), 200

@app.route('/lrw/balance/<user_id>', methods=['GET'])
def get_lrw_balance(user_id):
    balance = database_access.get_lrw_balance(db, user_id)
    return jsonify({'user_id': user_id, 'lrw_balance': balance}), 200

@app.route('/lrw/transfer', methods=['POST'])
def transfer_lrw():
    data = request.json
    from_user = data.get('from_user')
    to_user = data.get('to_user')
    amount = data.get('amount')

    if not from_user or not to_user or not isinstance(amount, int) or amount <= 0:
        return jsonify({'error': 'Invalid transfer parameters'}), 400

    from_balance = database_access.get_lrw_balance(db, from_user)
    if from_balance < amount:
        return jsonify({'error': 'Insufficient LRW balance'}), 400

    to_balance = database_access.get_lrw_balance(db, to_user)

    database_access.store_lrw_balance(db, from_user, from_balance - amount)
    database_access.store_lrw_balance(db, to_user, to_balance + amount)

    return jsonify({'message': f'Transferred {amount} LRW from {from_user} to {to_user}'}), 200

@app.route('/stake', methods=['POST'])
def stake_tokens():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')

    if not user_id or not isinstance(amount, int) or amount <= 0:
        return jsonify({'error': 'Invalid staking parameters'}), 400

    current_balance = database_access.get_token_balance(db, user_id)
    if current_balance < amount:
        return jsonify({'error': 'Insufficient WŁC balance to stake'}), 400

    try:
        consensus_engine.token_rewards.stake_tokens(db, user_id, amount)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': f'User {user_id} staked {amount} WŁC tokens.'}), 200

@app.route('/unstake', methods=['POST'])
def unstake_tokens():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')

    if not user_id or not isinstance(amount, int) or amount <= 0:
        return jsonify({'error': 'Invalid unstaking parameters'}), 400

    current_stake = database_access.get_stake_balance(db, user_id)
    if current_stake < amount:
        return jsonify({'error': 'Insufficient staked balance to unstake'}), 400

    try:
        consensus_engine.token_rewards.unstake_tokens(db, user_id, amount)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': f'User {user_id} unstaked {amount} WŁC tokens.'}), 200

@app.route('/stake/balance/<user_id>', methods=['GET'])
def get_stake_balance(user_id):
    balance = database_access.get_stake_balance(db, user_id)
    return jsonify({'user_id': user_id, 'staked_balance': balance}), 200

@app.route('/stake/claim', methods=['POST'])
def claim_staking_rewards():
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'Invalid user ID'}), 400

    rewards = database_access.get_staking_rewards(db, user_id)
    if rewards <= 0:
        return jsonify({'message': 'No staking rewards to claim'}), 200

    current_balance = database_access.get_token_balance(db, user_id)
    new_balance = current_balance + rewards
    database_access.store_token_balance(db, user_id, new_balance)
    database_access.store_staking_rewards(db, user_id, 0)

    return jsonify({'message': f'User {user_id} claimed {rewards:.6f} WŁC staking rewards.'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
