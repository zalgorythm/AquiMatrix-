"""
Module to handle token rewards for miners in the consensus engine.
"""

from lib import database_access
import json
import logging
import os

logger = logging.getLogger('token_rewards')

# Load pof_parameters from JSON config file
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'pof_parameters.json')
with open(config_path, 'r') as f:
    pof_parameters = json.load(f)

def reward_miner(db, miner_id):
    """
    Reward the miner with tokens for successfully mining an entry.
    """
    tokenomics = pof_parameters.get('tokenomics', {})
    reward_amount = tokenomics.get('initial_reward', 50)

    # Calculate 5% of reward to funnel into vault
    vault_share = int(reward_amount * 0.05)
    miner_share = reward_amount - vault_share

    # Get current balances
    current_balance = database_access.get_token_balance(db, miner_id) or 0
    vault_balance = database_access.get_vault_balance(db) or 0

    # Update miner balance
    new_balance = current_balance + miner_share
    database_access.store_token_balance(db, miner_id, new_balance)

    # Update vault balance
    new_vault_balance = vault_balance + vault_share
    database_access.store_vault_balance(db, new_vault_balance)

    logger.info(f"Rewarded miner {miner_id} with {miner_share} WŁC tokens. New balance: {new_balance}")
    logger.info(f"Added {vault_share} WŁC tokens to vault. New vault balance: {new_vault_balance}")

def mint_liquid_reward_tokens(db, usdt_amount, recipient_id):
    """
    Mint LiquidRewardWaclainium (LRW) tokens proportional to USDT donations.
    """
    # Assume 1 USDT = 1 LRW for simplicity
    lrw_amount = usdt_amount

    # Get current LRW balance
    current_lrw_balance = database_access.get_lrw_balance(db, recipient_id) or 0

    # Update LRW balance
    new_lrw_balance = current_lrw_balance + lrw_amount
    database_access.store_lrw_balance(db, recipient_id, new_lrw_balance)

    logger.info(f"Minted {lrw_amount} LRW tokens to {recipient_id}. New LRW balance: {new_lrw_balance}")

def stake_tokens(db, user_id, amount):
    """
    Stake WŁC tokens to earn 5% APR rewards.
    """
    current_balance = database_access.get_token_balance(db, user_id)
    if current_balance < amount:
        raise ValueError("Insufficient WŁC balance to stake")

    current_stake = database_access.get_stake_balance(db, user_id)
    new_stake = current_stake + amount
    database_access.store_stake_balance(db, user_id, new_stake)

    new_balance = current_balance - amount
    database_access.store_token_balance(db, user_id, new_balance)

    logger.info(f"User {user_id} staked {amount} WŁC tokens. New stake: {new_stake}, New balance: {new_balance}")

def unstake_tokens(db, user_id, amount):
    """
    Unstake WŁC tokens.
    """
    current_stake = database_access.get_stake_balance(db, user_id)
    if current_stake < amount:
        raise ValueError("Insufficient staked balance to unstake")

    current_balance = database_access.get_token_balance(db, user_id)
    new_stake = current_stake - amount
    database_access.store_stake_balance(db, user_id, new_stake)

    new_balance = current_balance + amount
    database_access.store_token_balance(db, user_id, new_balance)

    logger.info(f"User {user_id} unstaked {amount} WŁC tokens. New stake: {new_stake}, New balance: {new_balance}")

def distribute_staking_rewards(db):
    """
    Distribute 5% APR staking rewards to all stakers.
    This function should be called periodically (e.g., daily).
    """
    APR = 0.05
    # For simplicity, assume daily distribution: daily_rate = APR / 365
    daily_rate = APR / 365

    if not hasattr(db, 'stake_balances'):
        return

    for user_id, stake_amount in db.stake_balances.items():
        reward = stake_amount * daily_rate
        current_rewards = database_access.get_staking_rewards(db, user_id)
        new_rewards = current_rewards + reward
        database_access.store_staking_rewards(db, user_id, new_rewards)
        logger.info(f"Distributed {reward:.6f} staking rewards to {user_id}. Total rewards: {new_rewards:.6f}")
