import curses
from web3 import Web3
import time
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

privatekeys = os.getenv("PRIVATE_KEY")

rpc_urls = {
    'sepolia': 'https://ethereum-sepolia-rpc.publicnode.com',
    'arb-sepolia': os.getenv("ARB_RPC"),
    'base-sepolia': os.getenv("BASE_RPC"),
    'opt-sepolia': os.getenv("OP_RPC"),
    'blast-sepolia': os.getenv("BLAST_RPC"),
    'brn': 'https://brn.rpc.caldera.xyz/http'
}

web3_instances = {name: Web3(Web3.HTTPProvider(url)) for name, url in rpc_urls.items()}
for name, web3 in web3_instances.items():
    if not web3.is_connected():
        print(f"Warning: Cannot connect to the {name} network")
        web3_instances[name] = None 

addresses = {
    'ASC': web3_instances['sepolia'].eth.account.from_key(privatekeys).address
}

def get_balance(web3, address):
    if web3 is None:
        return 0
    balance_wei = web3.eth.get_balance(address)
    balance_ether = web3.from_wei(balance_wei, 'ether') 
    return balance_ether

def draw_timer(stdscr, remaining, row):
    timer_str = f" Bridge in {remaining} Seconds"
    stdscr.addstr(row, (curses.COLS - len(timer_str)) // 2, timer_str)

def draw_table(stdscr, start_y, start_x, chains_data, brn_balance, brn_change):
    stdscr.addstr(start_y, start_x, "+" + "-" * 48 + "+")
    stdscr.addstr(start_y + 1, start_x + 1, "|                AIRDROP ASC                   |")
    stdscr.addstr(start_y + 2, start_x, "+" + "-" * 48 + "+")

    # Display balances in a structured format
    stdscr.addstr(start_y + 3, start_x + 1, f"| ARB SEPOLIA    :  {chains_data['arb-sepolia']:.5f} ETH                |")
    stdscr.addstr(start_y + 4, start_x + 1, f"| OPT SEPOLIA    :  {chains_data['opt-sepolia']:.5f} ETH               |")
    stdscr.addstr(start_y + 5, start_x + 1, f"| BASE SEPOLIA   :  {chains_data['base-sepolia']:.5f} ETH                |")
    stdscr.addstr(start_y + 6, start_x + 1, f"| BLAST SEPOLIA  :  {chains_data['blast-sepolia']:.5f} ETH               |")
    stdscr.addstr(start_y + 7, start_x + 1, f"| TOTAL BRN      :  {brn_balance:.5f} BRN             |")
    stdscr.addstr(start_y + 8, start_x, "+" + "-" * 48 + "+")
    stdscr.addstr(start_y + 9, start_x + 1, f"| REWARD BRN     :  {brn_change:.5f} BRN                |")
    stdscr.addstr(start_y + 10, start_x, "+" + "-" * 48 + "+")

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)

    refresh_interval = 10  # seconds
    previous_balances = {name: 0 for name in ['arb-sepolia', 'base-sepolia', 'opt-sepolia', 'blast-sepolia']}
    previous_brn_balance = 0  # Initialize previous BRN balance

    while True:
        stdscr.clear()

        # Define table dimensions based on terminal size
        box_height = 12  # Total rows for display
        box_width = 50
        start_y = (curses.LINES - box_height) // 2
        start_x = (curses.COLS - box_width) // 2

        chains_data = {}

        # Display balances for all chains
        for chain_name, web3 in web3_instances.items():
            if web3 is None:
                continue
            
            balance = get_balance(web3, addresses['ASC'])
            chains_data[chain_name] = balance

            # Check if the balance has decreased and trigger subprocess if necessary
            if chain_name in previous_balances:
                if balance < previous_balances[chain_name]:
                    # Trigger the appropriate subprocess
                    try:
                        # Start subprocesses based on the chain name
                        if chain_name == 'arb-sepolia':
                            subprocess.Popen(['python', 'nwrk/arb.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif chain_name == 'opt-sepolia':
                            subprocess.Popen(['python', 'nwrk/op.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif chain_name == 'base-sepolia':
                            subprocess.Popen(['python', 'nwrk/base.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif chain_name == 'blast-sepolia':
                            subprocess.Popen(['python', 'nwrk/blast.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except Exception as e:
                        stdscr.addstr(start_y + 11, start_x, f"Error: {e}")

            # Update previous balances
            previous_balances[chain_name] = balance
        
        # Handle BRN separately
        if 'brn' in web3_instances:
            current_brn_balance = get_balance(web3_instances['brn'], addresses['ASC'])
            chains_data['brn'] = current_brn_balance
            brn_change = current_brn_balance - previous_brn_balance
            previous_brn_balance = current_brn_balance  # Update previous BRN balance 
        else:
            brn_change = 0  # Default if BRN isn't available
        
        draw_table(stdscr, start_y, start_x, chains_data, current_brn_balance, brn_change)

        # Countdown timer below the REWARD BRN
        row = start_y + 11  # Adjusting the row for timer display
        for remaining in range(refresh_interval, 0, -1):
            draw_timer(stdscr, remaining, row)
            stdscr.refresh()
            time.sleep(1)

        stdscr.refresh()

curses.wrapper(main)
