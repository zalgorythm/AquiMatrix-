import unittest
from unittest.mock import MagicMock
import sys
import os

# Adjust sys.path to import modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import consensus_engine.token_rewards as token_rewards
import lib.database_access as database_access

class TestStakingAndLRW(unittest.TestCase):
    def setUp(self):
        # Mock database as a simple object with dict attributes
        self.db = MagicMock()
        self.db.token_balances = {}
        self.db.lrw_balances = {}
        self.db.stake_balances = {}
        self.db.staking_rewards = {}
        self.db.vault_balance = 0

    def test_mint_liquid_reward_tokens(self):
        user_id = "user1"
        usdt_amount = 1000
        token_rewards.mint_liquid_reward_tokens(self.db, usdt_amount, user_id)
        self.assertEqual(database_access.get_lrw_balance(self.db, user_id), usdt_amount)

    def test_stake_and_unstake_tokens(self):
        user_id = "user2"
        initial_balance = 5000
        database_access.store_token_balance(self.db, user_id, initial_balance)

        # Stake 1000 tokens
        token_rewards.stake_tokens(self.db, user_id, 1000)
        self.assertEqual(database_access.get_stake_balance(self.db, user_id), 1000)
        self.assertEqual(database_access.get_token_balance(self.db, user_id), initial_balance - 1000)

        # Unstake 500 tokens
        token_rewards.unstake_tokens(self.db, user_id, 500)
        self.assertEqual(database_access.get_stake_balance(self.db, user_id), 500)
        self.assertEqual(database_access.get_token_balance(self.db, user_id), initial_balance - 500)

        # Unstake more than staked should raise error
        with self.assertRaises(ValueError):
            token_rewards.unstake_tokens(self.db, user_id, 600)

    def test_distribute_staking_rewards(self):
        user_id = "user3"
        stake_amount = 10000
        database_access.store_stake_balance(self.db, user_id, stake_amount)
        database_access.store_staking_rewards(self.db, user_id, 0)

        token_rewards.distribute_staking_rewards(self.db)
        rewards = database_access.get_staking_rewards(self.db, user_id)
        expected_reward = stake_amount * 0.05 / 365
        self.assertAlmostEqual(rewards, expected_reward, places=6)

    def test_vault_balance_update(self):
        initial_vault_balance = database_access.get_vault_balance(self.db)
        miner_id = "miner1"
        database_access.store_token_balance(self.db, miner_id, 0)

        # Reward miner and check vault balance increase
        token_rewards.reward_miner(self.db, miner_id)
        new_vault_balance = database_access.get_vault_balance(self.db)
        self.assertGreater(new_vault_balance, initial_vault_balance)

if __name__ == '__main__':
    unittest.main()
