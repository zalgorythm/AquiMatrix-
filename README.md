# AquiMatrix

AquiMatrix is a blockchain-inspired platform featuring a mining simulation, REST API, and WebSocket server for real-time updates. It provides SDKs and CLI tools for interacting with the network, submitting entries, querying state, and monitoring node status.

## Features

- Mining simulation with real-time status updates via WebSocket
- REST API for entry submission, state queries, and DAG information
- Command-line interface (CLI) for account management, entry submission, and monitoring
- Python SDK for programmatic interaction with the network
- Modular architecture with consensus engine, VM, and data ingestion components

## Installation

Ensure you have Python 3.8+ installed.

Install required Python packages:

```bash
pip install -r requirements.txt
```

## Running the Project

You can start the services individually or use the provided `quickstart.sh` script.

### Start REST API Server

```bash
python api_gateway/rest_endpoints.py
```

This starts the REST API server on port 9000.

### Start WebSocket Server

```bash
python api_gateway/websocket_server.py
```

This starts the WebSocket server on port 9001.

### Start Mining Simulator

```bash
python mining_backend.py
```

This connects to the WebSocket server and simulates mining status broadcasts.

### Quick Start

Run the `quickstart.sh` script to start all services in the background:

```bash
./quickstart.sh
```

## Usage

### CLI Commands

Use the CLI tool to interact with the network:

```bash
python client_interfaces/cli_commands.py <command> [args]
```

Available commands:

- `create-account`: Generate a new account keypair
- `submit-entry <entry_file>`: Submit an entry JSON file
- `get-state <address>`: Query contract state by address
- `status`: Show node status
- `get-dag-tips`: List DAG tip entries
- `get-state-root`: Show current state root hash
- `mining-dashboard`: Launch mining dashboard
- `audit-report`: Generate audit report

### Python SDK

Use the Python SDK to interact programmatically:

```python
from client_interfaces.python_sdk import AquiMatrixClient

client = AquiMatrixClient(api_url="http://localhost:9000")
response = client.submit_entry(entry)
state = client.get_state(address)
```

## Testing

Run unit and integration tests using pytest:

```bash
pytest tests/
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Tokenomics

### Wacłainium (WŁC) Token

- **Earning Wacłainium:** Wacłainium tokens are earned primarily through mining rewards. Miners receive an initial reward of 50 WŁC tokens per successfully mined entry, with rewards subject to halving intervals and decay factors as defined in the protocol parameters.
- **Fixed Supply:** The total supply of Wacłainium is capped at 1,000,000,000 tokens, ensuring scarcity and value preservation.
- **Staking APR:** Holders can stake their Wacłainium tokens to earn an annual percentage rate (APR) of 5%. This incentivizes long-term holding and network participation.
- **Token Burning:** A portion of tokens is burned with each transaction and smart contract operation, reducing circulating supply and supporting token value.

### Market Value Liquidity Vault

- **Vault Funding:** 5% of all earned mining rewards are automatically funneled into a dedicated market value liquidity vault.
- **USDT Pairing:** The vault pairs bridged USDT with Wacłainium tokens, creating a liquidity pool that supports price stability.
- **Community Donations:** Anyone can donate USDT to the vault to help raise the price of Wacłainium. Donations mint a new reward token called *LiquidRewardWaclainium*, which can be traded but cannot be used for smart contracts, representing a staked position in the vault.
- **Price Calculation:** The direct price of Wacłainium is determined by multiplying the total amount of WŁC tokens by the amount of USDT held in the vault.
- **Non-Tradable Vault:** The vault itself is not tradable, serving solely as a liquidity and price support mechanism.

## Tokenomics Projections

This section provides projections and mathematical analysis of the tokenomics of AquiMatrix, including mining rewards, staking returns, vault funding, and price dynamics.

### Mining Rewards Projection

- Initial mining reward: 50 WŁC per entry
- Reward halving interval: 210,000 entries
- Reward decay factor: 0.5
- Minimum reward: 1 WŁC
- Total fixed supply: 1,000,000,000 WŁC

Assuming a constant entry rate, mining rewards decrease by half every 210,000 entries until the minimum reward is reached. The total supply cap ensures scarcity.

### Staking Rewards Projection

- Annual Percentage Rate (APR): 5%
- Staking rewards are paid from inflation and network fees.
- For example, staking 10,000 WŁC yields 500 WŁC annually.

### Vault Funding and Price Dynamics

- 5% of all mining rewards are funneled into the market value liquidity vault.
- The vault holds bridged USDT paired with WŁC tokens.
- Donations of USDT mint *LiquidRewardWaclainium* tokens, representing staked positions.

### Price Calculation

- The price of Wacłainium (WŁC) is approximated as:

  \[
  \text{Price}_{WŁC} = \frac{\text{Total USDT in Vault}}{\text{Total WŁC Supply}}
  \]

- Donations increase USDT in the vault, raising the price.
- The vault is non-tradable, providing price stability.

### Example Projection

- If the vault holds 1,000,000 USDT and total WŁC supply is 1,000,000,000 tokens:

  \[
  \text{Price}_{WŁC} = \frac{1,000,000}{1,000,000,000} = 0.001 \text{ USDT per WŁC}
  \]

- If a user donates 100,000 USDT, the vault increases to 1,100,000 USDT, raising the price proportionally.

### Impact of LiquidRewardWaclainium

- LiquidRewardWaclainium tokens are minted proportional to USDT donations.
- These tokens are tradable but cannot be used in smart contracts.
- They represent staked positions in the vault, providing liquidity incentives.

This projection helps stakeholders understand the economic incentives and potential growth of the AquiMatrix ecosystem.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
