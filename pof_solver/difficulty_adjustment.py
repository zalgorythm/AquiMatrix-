"""
difficulty_adjustment.py

Dynamically tunes the PoF difficulty to maintain a stable entry rate across the network.
Operations:
1. Solve Time Monitoring: Tracks average solve time over last M entries.
2. Target Adjustment: Updates hash target every M entries to achieve target solve time τ.
3. Pattern Parameter Tuning: Adjusts bit-length (k) and mismatch tolerance (δ) based on network metrics.
Interacts with database_access.py to store historical difficulty data.
"""

import time
import logging
from lib import database_access
import json
import logging
import os

logger = logging.getLogger('difficulty_adjustment')

# Load pof_parameters from JSON config file
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'pof_parameters.json')
with open(config_path, 'r') as f:
    pof_parameters = json.load(f)

class DifficultyAdjustment:
    def __init__(self, db):
        self.db = db
        self.M = pof_parameters.get('adjustment_interval', 100)
        self.target_solve_time = pof_parameters.get('target_solve_time', 10)
        self.current_target = None
        self.k = pof_parameters.get('bit_length', 64)
        self.delta = pof_parameters.get('mismatch_tolerance', 5)

    def get_average_solve_time(self):
        """
        Calculate average solve time over last M entries.
        """
        timestamps = database_access.get_last_m_timestamps(self.db, self.M)
        if len(timestamps) < 2:
            return None
        intervals = [t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:])]
        avg_time = sum(intervals) / len(intervals)
        return avg_time

    def adjust_target(self):
        """
        Adjust difficulty target based on average solve time.
        """
        avg_time = self.get_average_solve_time()
        if avg_time is None:
            logger.info("Not enough data to adjust difficulty")
            return

        if avg_time > self.target_solve_time:
            # Decrease difficulty (increase target)
            self.current_target = int(self.current_target * 1.1)
            logger.info(f"Increasing target difficulty to {self.current_target}")
        else:
            # Increase difficulty (decrease target)
            self.current_target = int(self.current_target * 0.9)
            logger.info(f"Decreasing target difficulty to {self.current_target}")

        # Adjust pattern parameters if needed (placeholder)
        # self.k, self.delta = self.tune_pattern_parameters()

        database_access.store_difficulty(self.db, self.current_target, self.k, self.delta)

    def tune_pattern_parameters(self):
        """
        Adjust bit-length and mismatch tolerance based on network metrics.
        Placeholder for actual tuning logic.
        """
        # Example: adjust k and delta based on network hash rate or solver performance
        return self.k, self.delta
