import curses
from web3 import Web3
import time
import subprocess
import shutil
import os
from dotenv import load_dotenv

load_dotenv()

privatekeys = os.getenv("PRIVATE_KEY")

# List of Python executables to try
python_executables = ['python', 'python3', 'py']

rpc_urls = {
    'sepolia': 'https://ethereum-sepolia-rpc.publicnode.com',
    'arb-sepolia': os.getenv("ARB_RPC"),
    'base-sepolia': os.getenv("BASE_RPC"),
    'opt-sepolia': os.getenv("OP_RPC"),
    'blast-sepolia': os.getenv("BLAST_RPC"),
    'brn': 'https://brn.rpc.caldera.xyz/http'
}

# Create web3 instances for each network
web3_instances = {name: Web3(Web3.HTTPProvider(url)) for name, url in rpc_urls.items()}
for name, web3 in web3_instances.items():
    if not web3.is_connected():
        print(f"Warning: Cannot connect to the {name} network")
        web3_instances[name] = None 

addresses = {
    'ASC': web3_instances['sepolia'].eth.account.from_key(privatekeys).address
}

def get_balance(web3, address):
    """Get the balance in Ether for a given address."""
    if web3 is None:
        return 0
    balance_wei = web3.eth.get_balance(address)
    balance_ether = web3.from_wei(balance_wei, 'ether')
    return balance_ether

def calculate_change(new_balance, old_balance):
    """Calculate the change in balance."""
    return new_balance - old_balance

def print_banner(stdscr):
    """Print the banner at a fixed position."""
    stdscr.addstr(0, 0, "                █████████   █████ ███████████   ██████████   ███████████      ███████    ███████████       █████████    █████████    █████████", curses.color_pair(1))
    stdscr.addstr(1, 0, "               ███░░░░░███ ░░███ ░░███░░░░░███ ░░███░░░░███ ░░███░░░░░███   ███░░░░░███ ░░███░░░░░███     ███░░░░░███  ███░░░░░███  ███░░░░░███", curses.color_pair(1))
    stdscr.addstr(2, 0, "              ░███    ░███  ░███  ░███    ░███  ░███   ░░███ ░███    ░███  ███     ░░███ ░███    ░███    ░███    ░███ ░███    ░░░  ███     ░░░", curses.color_pair(1))
    stdscr.addstr(3, 0, "              ░███████████  ░███  ░██████████   ░███    ░███ ░██████████  ░███      ░███ ░██████████     ░███████████ ░░█████████ ░███         ", curses.color_pair(1))
    stdscr.addstr(4, 0, "              ░███░░░░░███  ░███  ░███░░░░░███  ░███    ░███ ░███░░░░░███ ░███      ░███ ░███░░░░░░      ░███░░░░░███  ░░░░░░░░███░███         ", curses.color_pair(1))
    stdscr.addstr(5, 0, "              ░███    ░███  ░███  ░███    ░███  ░███    ███  ░███    ░███ ░░███     ███  ░███            ░███    ░███  ███    ░███░░███     ███", curses.color_pair(1))
    stdscr.addstr(6, 0, "              █████   █████ █████ █████   █████ ██████████   █████   █████ ░░░███████░   █████           █████   █████░░█████████  ░░█████████", curses.color_pair(1))
    stdscr.addstr(7, 0, "              ░░░░░   ░░░░░ ░░░░░ ░░░░░   ░░░░░ ░░░░░░░░░░   ░░░░░   ░░░░░    ░░░░░░░    ░░░░░           ░░░░░   ░░░░░  ░░░░░░░░░    ░░░░░░░░░  ", curses.color_pair(1))
    stdscr.addstr(8, 0, "                                                              ===============================================", curses.color_pair(1))
    stdscr.addstr(9, 0, "                                                               |   Telegram Channel : @airdropasc          |   ", curses.color_pair(1))
    stdscr.addstr(10, 0, "                                                               |   Telegram Group   : @autosultan_group    |    ", curses.color_pair(1))
    stdscr.addstr(11, 0, "                                                              ===============================================", curses.color_pair(1))

def draw_table(stdscr, start_y, start_x, chains_data, brn_balance, brn_change, col_width):
    """Draw the table with chain balances and rewards."""
    stdscr.addstr(start_y, start_x, "+" + "-" * (col_width - 1) + "+")
    stdscr.addstr(start_y + 1, start_x + 1, "|                AIRDROP ASC                    |")
    stdscr.addstr(start_y + 2, start_x, "+" + "-" * (col_width - 1) + "+")

    # Display balances in a structured format
    stdscr.addstr(start_y + 3, start_x + 1, f"| ARB SEPOLIA    :  {chains_data['arb-sepolia']:.5f} ETH                |")
    stdscr.addstr(start_y + 4, start_x + 1, f"| OPT SEPOLIA    :  {chains_data['opt-sepolia']:.5f} ETH                |")
    stdscr.addstr(start_y + 5, start_x + 1, f"| BASE SEPOLIA   :  {chains_data['base-sepolia']:.5f} ETH                |")
    stdscr.addstr(start_y + 6, start_x + 1, f"| BLAST SEPOLIA  :  {chains_data['blast-sepolia']:.5f} ETH                |")
    stdscr.addstr(start_y + 7, start_x + 1, f"| TOTAL BRN      :  {brn_balance:.5f} BRN              |")
    stdscr.addstr(start_y + 8, start_x + 1, f"| REWARD BRN     :  {brn_change:.5f} BRN                 |")
    stdscr.addstr(start_y + 9, start_x, "+" + "-" * (col_width - 1) + "+")

def main(stdscr):
    """Main function for the curses application."""
    curses.curs_set(0)  
    stdscr.nodelay(1) 
    stdscr.timeout(1000)

    # Color pair for the banner
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

    previous_balances = {} 
    previous_brn_balance = 0
    refresh_interval = 10

    # Print the banner once at the start
    print_banner(stdscr)

    while True:
        stdscr.clear()

        # Reprint the banner in each iteration
        print_banner(stdscr)

        max_y, max_x = stdscr.getmaxyx()

        # Set column width for the table
        col_width = 50  # Adjust as needed

        # Center the table vertically
        start_y = 12  # Start below the banner
        start_x = (max_x - col_width) // 2   # Center the table horizontally

        chains_data = {name: get_balance(web3, addresses['ASC']) for name, web3 in web3_instances.items() if web3}

        # Trigger subprocess if balances exceed 0.2
        for chain_name, balance in chains_data.items():
            if balance > 0.2:
                for python_exec in python_executables:
                    if shutil.which(python_exec) is not None:
                        script_map = {
                            'arb-sepolia': "nwrk/arb.py",
                            'opt-sepolia': "nwrk/op.py",
                            'base-sepolia': "nwrk/base.py",
                            'blast-sepolia': "nwrk/blast.py"
                        }
                        if chain_name in script_map:
                            try:
                                subprocess.Popen([python_exec, script_map[chain_name]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            except Exception as e:
                                print(f"Failed to run with {python_exec}: {e}")

        # Handle BRN balances
        if 'brn' in web3_instances and web3_instances['brn'] is not None:
            current_brn_balance = get_balance(web3_instances['brn'], addresses['ASC'])
            brn_change = calculate_change(current_brn_balance, previous_brn_balance)
            previous_brn_balance = current_brn_balance
        else:
            current_brn_balance = 0
            brn_change = 0

        # Draw the table
        draw_table(stdscr, start_y, start_x, chains_data, current_brn_balance, brn_change, col_width)

        # Position for the refreshing message
        refresh_y = start_y + 10  # Adjusted position below the table
        refresh_msg = "Starting Bridge in"
        stdscr.addstr(refresh_y, (max_x - len(refresh_msg) - 3) // 2, refresh_msg)

        for remaining in range(refresh_interval, 0, -1):
            stdscr.addstr(refresh_y, (max_x - len(refresh_msg) - 3) // 2 + len(refresh_msg) + 1, str(remaining).center(2))  # Show remaining time
            stdscr.refresh()
            time.sleep(1)

        stdscr.refresh()

curses.wrapper(main)
