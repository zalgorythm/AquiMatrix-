import asyncio
import websockets
import json
import os
import sys
import time
import argparse
import logging
from .malformed_json_parser import parse_malformed_json
from colorama import init, Fore, Style

init(autoreset=True)

ART = r"""
████████╗██████╗ ██╗ █████╗ ██████╗     ███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗
╚══██╔══╝██╔══██╗██║██╔══██╗██╔══██╗    ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝
██║   ██████╔╝██║███████║██║  ██║    ██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝
██║   ██╔══██╗██║██╔══██║██║  ██║    ██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ██╔██╗
██║   ██║  ██║██║██║  ██║██████╔╝    ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗
╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
"""

class MiningDashboard:
    def __init__(self, uri="ws://localhost:9001", max_retries=5):
        self.uri = uri
        self.status = {
            "status": "UNKNOWN",
            "target": "N/A",
            "nonce": 0,
            "time": "00:00:00",
            "hashrate": 0,
            "pof_stage_1": 0,
            "pof_stage_2": 0,
            "confirmation_levels": {
                "L0": 0,
                "L1": 0,
                "L2": 0,
                "L3": 0
            },
            "balance": 0.0,
            "today_mining": 0.0,
            "pending_rewards": 0.0,
            "fees_paid": 0.0
        }
        self.max_retries = max_retries
        self.retry_count = 0
        self.should_exit = False
        self.logger = logging.getLogger("MiningDashboard")
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        self.clear_screen()
        print(Fore.CYAN + ART)
        print(Fore.GREEN + "\nMINING DASHBOARD\n" + Style.RESET_ALL)
        print(f"Status: {Fore.YELLOW}{self.status['status']}{Style.RESET_ALL}")
        print(f"Target: {Fore.YELLOW}{self.status['target']}{Style.RESET_ALL}")
        print(f"Nonce: {Fore.YELLOW}{self.status['nonce']}{Style.RESET_ALL}")
        print(f"Time: {Fore.YELLOW}{self.status['time']}{Style.RESET_ALL}")
        print(f"Hashrate: {Fore.YELLOW}{self.status['hashrate']}{Style.RESET_ALL}")
        print(f"PoF Stage 1: {Fore.YELLOW}{self.status['pof_stage_1']}%{Style.RESET_ALL}")
        print(f"PoF Stage 2: {Fore.YELLOW}{self.status['pof_stage_2']}%{Style.RESET_ALL}")
        print("Confirmation Levels:")
        for level, count in self.status['confirmation_levels'].items():
            print(f"  {level}: {Fore.YELLOW}{count}{Style.RESET_ALL}")
        print(f"Balance: {Fore.YELLOW}{self.status['balance']}{Style.RESET_ALL}")
        print(f"Today's Mining: {Fore.YELLOW}{self.status['today_mining']}{Style.RESET_ALL}")
        print(f"Pending Rewards: {Fore.YELLOW}{self.status['pending_rewards']}{Style.RESET_ALL}")
        print(f"Fees Paid: {Fore.YELLOW}{self.status['fees_paid']}{Style.RESET_ALL}")
        print(Fore.GREEN + "\nPress Ctrl+C to exit." + Style.RESET_ALL)

    async def connect(self):
        while not self.should_exit and (self.retry_count < self.max_retries):
            try:
                async with websockets.connect(self.uri) as websocket:
                    self.logger.info(f"Connected to websocket server at {self.uri}")
                    self.retry_count = 0
                    # Subscribe to mining status event
                    subscribe_msg = json.dumps({"action": "subscribe", "event": "mining_status"})
                    await websocket.send(subscribe_msg)
                    self.logger.info(f"Sent subscription message: {subscribe_msg}")
                    async for message in websocket:
                        if self.should_exit:
                            break
                        self.logger.debug(f"Received message: {message}")
                        try:
                            data = parse_malformed_json(message)
                            if isinstance(data, dict):
                                self.status.update(data)
                            self.render()
                        except Exception as e:
                            self.logger.error(f"Error parsing message: {e} for message: {message}")
            except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError) as e:
                self.retry_count += 1
                self.logger.warning(f"Connection error: {e}. Retry {self.retry_count}/{self.max_retries} in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(5)
        if self.retry_count >= self.max_retries:
            self.logger.error("Max retries reached. Exiting.")

    def stop(self):
        self.should_exit = True

def main():
    parser = argparse.ArgumentParser(description="Mining Dashboard WebSocket Client")
    parser.add_argument("--uri", type=str, default="ws://localhost:9001", help="WebSocket server URI")
    parser.add_argument("--max-retries", type=int, default=5, help="Maximum number of connection retries")
    args = parser.parse_args()

    dashboard = MiningDashboard(uri=args.uri, max_retries=args.max_retries)
    dashboard.render()

    try:
        asyncio.run(dashboard.connect())
    except KeyboardInterrupt:
        dashboard.stop()
        print("\nExiting mining dashboard...")

if __name__ == "__main__":
    main()
