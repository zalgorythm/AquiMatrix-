import json

status = {
    "status": "Mining",
    "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "nonce": 65,
    "time": "00:48:54",
    "hashrate": 242,
    "pof_stage_1": 50,
    "pof_stage_2": 75,
    "confirmation_levels": {
        "L0": 10,
        "L1": 5,
        "L2": 2,
        "L3": 1
    },
    "balance": 0.0,
    "today_mining": 0.0,
    "pending_rewards": 0.0,
    "fees_paid": 0.0,
    "ledger_updated": True
}

json_str = json.dumps(status)
print(json_str)
