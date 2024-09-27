from web3 import Web3
from eth_account import Account
import time
import sys
import os
import random
from data_hex import Data_HEX
from privateKeys import private_keys, VALUE_ETH, GAS_LIMIT_ADJUSTMENT, FEE_GWEI
from decimal import Decimal

# Define network details
networks = {
    'Arbitrum Sepolia': {
        'rpc_url': 'https://arbitrum-sepolia.blockpi.network/v1/rpc/public',
        'chain_id': 421614,
        'contract_address': '0x8D86c3573928CE125f9b2df59918c383aa2B514D'
    },
    'OP Sepolia': {
        'rpc_url': 'https://sepolia.optimism.io',
        'chain_id': 11155420,
        'contract_address': '0xF221750e52aA080835d2957F2Eed0d5d7dDD8C38'
    },
    'Blast Sepolia': {
        'rpc_url': 'https://blast-sepolia.blockpi.network/v1/rpc/public',
        'chain_id': 168587773,
        'contract_address': '0x1D5FD4ed9bDdCCF5A74718B556E9d15743cB26A2'
    },
    'Base Sepolia': {
        'rpc_url': 'https://base-sepolia-rpc.publicnode.com',
        'chain_id': 84532,
        'contract_address': '0x30A0155082629940d4bd9Cd41D6EF90876a0F1b5'
    }
}

def center_text(text):
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        terminal_width = 80  # Default width if terminal size cannot be determined
    lines = text.splitlines()
    centered_lines = [line.center(terminal_width) for line in lines]
    return "\n".join(centered_lines)

intro_text = """
    =========================================================
      AIRDROP ASC
    =========================================================
    Credit By       : Airdrop ASC
    Telegram Channel: @airdropasc
    Telegram Group  : @autosultan_group
    =========================================================
"""

def print_intro():
    os.system('clear') if os.name == 'posix' else os.system('cls')
    print("\033[96m" + center_text(intro_text) + "\033[0m")
    print("\n")

def get_current_gas_price(web3):
    try:
        gas_price_wei = web3.eth.gas_price
        gas_price_gwei = web3.from_wei(gas_price_wei, 'gwei')
        return gas_price_gwei
    except Exception as e:
        print(f"Error fetching gas price: {e}")
        return Decimal('0')

def send_bridge_transaction(web3, account, data, network_name, nonce):
    try:
        value_in_ether = float(VALUE_ETH)
        value_in_wei = web3.to_wei(value_in_ether, 'ether')

        gas_estimate = web3.eth.estimate_gas({
            'to': networks[network_name]['contract_address'],
            'from': account.address,
            'data': data,
            'value': value_in_wei
        })
        gas_limit = gas_estimate + GAS_LIMIT_ADJUSTMENT

        current_gas_price_gwei = Decimal(get_current_gas_price(web3))
        priority_fee_gwei = Decimal(FEE_GWEI)
        max_fee_gwei = current_gas_price_gwei + priority_fee_gwei

        base_fee = web3.to_wei(current_gas_price_gwei, 'gwei')
        priority_fee = web3.to_wei(priority_fee_gwei, 'gwei')

        transaction = {
            'nonce': nonce,
            'to': networks[network_name]['contract_address'],
            'value': value_in_wei,
            'gas': gas_limit,
            'maxFeePerGas': base_fee + priority_fee,
            'maxPriorityFeePerGas': priority_fee,
            'chainId': networks[network_name]['chain_id'],
            'data': data
        }

        signed_txn = web3.eth.account.sign_transaction(transaction, account.key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return web3.to_hex(tx_hash), value_in_ether
    except ValueError as e:
        print(f"Error sending transaction on {network_name}: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error sending transaction on {network_name}: {e}")
        return None, None

def validate_private_key(private_key):
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    if len(private_key) != 66:
        return None
    try:
        Account.from_key(private_key)
        return private_key
    except ValueError:
        return None

def create_tx_folder():
    base_folder = 'Tx_Hash'
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    return base_folder

def create_network_folder(base_folder, network_name):
    network_folder = os.path.join(base_folder, network_name.replace(' ', '-'))
    if not os.path.exists(network_folder):
        os.makedirs(network_folder)
    return network_folder

def create_bridge_file(network_folder, bridge_name):
    bridge_file_path = os.path.join(network_folder, f'Tx_{bridge_name.replace(" ", "-")}.txt')
    if not os.path.exists(bridge_file_path):
        open(bridge_file_path, 'w').close()  # Create an empty file
    return bridge_file_path

def save_tx_hash(tx_hash, source_network, dest_network):
    base_folder = create_tx_folder()
    source_folder = create_network_folder(base_folder, source_network)
    bridge_file_path = create_bridge_file(source_folder, f'{source_network} - {dest_network}')
    with open(bridge_file_path, 'a') as file:
        file.write(f'{tx_hash}\n')

def run_all_network(account):
    bridges = {
        'Arbitrum Sepolia': ["ARB - OP SEPOLIA", "ARB - BASE", "ARB - BLAST"],
        'OP Sepolia': ["OP - ARB", "OP - BASE", "OP - BLAST"],
        'Base Sepolia': ["BASE - ARB", "BASE - OP", "BASE - BLAST"],
        'Blast Sepolia': ["BLAST - ARB", "BLAST - OP", "BLAST - BASE"]
    }

    active_networks = {network: True for network in networks.keys()}

    while True:
        print("\n=== Select Networks to Disable ===")
        for idx, network in enumerate(networks.keys(), start=1):
            status = "\033[92mActive\033[0m" if active_networks[network] else "\033[91mInactive\033[0m"
            print(f"{idx}. {network} [{status}]")
        print(f"{len(networks) + 1}. Run Transaction")

        choice = input(f"Select network to toggle (1-{len(networks)}) or {len(networks)+1} to run transaction: ")

        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(networks):
                network_name = list(networks.keys())[choice - 1]
                active_networks[network_name] = not active_networks[network_name]
                new_status = "Inactive" if not active_networks[network_name] else "Active"
                # Clear screen and reprint menu without extra messages
                os.system('clear') if os.name == 'posix' else os.system('cls')
                print_intro()
            elif choice == len(networks) + 1:
                break
            else:
                print("Invalid choice. Please try again.")
                time.sleep(1)  # Brief pause before reprinting the menu
        else:
            print("Invalid input. Please enter a number.")
            time.sleep(1)  # Brief pause before reprinting the menu

    # Filter active networks
    selected_networks = [network for network, active in active_networks.items() if active]

    if not selected_networks:
        print("\033[91mNo networks selected to run. Exiting.\033[0m")
        time.sleep(2)
        sys.exit(0)

    try:
        print_intro()
        print(f"Running transactions on the following networks: {', '.join(selected_networks)}")
        total_success = 0
        for network_name in selected_networks:
            print(f"\n--- Processing {network_name} ---")
            web3 = Web3(Web3.HTTPProvider(networks[network_name]['rpc_url']))
            try:
                nonce = web3.eth.get_transaction_count(account.address)
            except Exception as e:
                print(f"\033[91mError fetching nonce for {network_name}: {e}\033[0m")
                continue
            for bridge in bridges[network_name]:
                try:
                    data = Data_HEX[bridge]
                    tx_hash, value_sent = send_bridge_transaction(web3, account, data, network_name, nonce)
                    nonce += 1  # Increment nonce locally

                    if tx_hash:
                        print(f"\033[92mTx Hash: {tx_hash}\nNetwork: {network_name} | Bridge: {bridge} | Amount: {value_sent} ETH\033[0m")
                        save_tx_hash(tx_hash, network_name, bridge)
                        total_success += 1
                    else:
                        print(f"\033[91mFailed to send transaction on {network_name} for bridge {bridge}.\033[0m")

                    time.sleep(random.uniform(4, 6))  # Delay antara 4-6 detik
                except KeyboardInterrupt:
                    print("\n\033[93mBot Stop\033[0m")
                    sys.exit(0)
                except Exception as e:
                    print(f"\033[91mError processing transaction on {network_name} for bridge {bridge}: {e}\033[0m")

        print(f"\n\n\033[92mAll Transactions Complete: Total {total_success}\033[0m")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\033[93mBot Stop\033[0m")
        sys.exit(0)

def main():
    try:
        print_intro()
        print("=== Main Menu ===")
        print("1. ARB (Arbitrum Sepolia)")
        print("2. OP (Optimism Sepolia)")
        print("3. BASE (Base Sepolia)")
        print("4. BLAST (Blast Sepolia)")
        print("5. Multi Bridge (Run all transactions for selected network)")
        print("6. Run All Network")
        print("==================\n")

        network_choice = input("Network choice (1-6): ")
        network_dict = {
            '1': 'Arbitrum Sepolia',
            '2': 'OP Sepolia',
            '3': 'Base Sepolia',
            '4': 'Blast Sepolia',
            '5': 'Multi Bridge',
            '6': 'Run All Network'
        }
        if network_choice not in network_dict:
            print("\033[91mInvalid choice.\033[0m")
            time.sleep(1)
            sys.exit(1)

        selected_network = network_dict[network_choice]

        # Clear the terminal after selection
        os.system('clear') if os.name == 'posix' else os.system('cls')
        print_intro()

        # Validate private key
        private_key = validate_private_key(private_keys[0])
        if not private_key:
            print("\033[91mInvalid private key format.\033[0m")
            sys.exit(1)
        account = Account.from_key(private_key)

        if selected_network == "Multi Bridge":
            print("\033[94mYou have selected Multi Bridge mode. Running transactions simultaneously for the selected network.\033[0m")
            bridges = {
                'Arbitrum Sepolia': ["ARB - OP SEPOLIA", "ARB - BASE", "ARB - BLAST"],
                'OP Sepolia': ["OP - ARB", "OP - BASE", "OP - BLAST"],
                'Base Sepolia': ["BASE - ARB", "BASE - OP", "BASE - BLAST"],
                'Blast Sepolia': ["BLAST - ARB", "BLAST - OP", "BLAST - BASE"]
            }

            print("\n=== Select Network for Multi Bridge ===")
            available_networks = [k for k in network_dict.values() if k not in ['Multi Bridge', 'Run All Network']]
            for i, network in enumerate(available_networks, start=1):
                print(f"{i}. {network}")
            print("========================================\n")

            multi_bridge_choice = input(f"Network choice for Multi Bridge (1-{len(available_networks)}): ")
            if not multi_bridge_choice.isdigit() or not (1 <= int(multi_bridge_choice) <= len(available_networks)):
                print("\033[91mInvalid choice.\033[0m")
                time.sleep(1)
                sys.exit(1)

            multi_network = available_networks[int(multi_bridge_choice) - 1]
            try:
                num_transactions = int(input("How many rounds do you want to repeat the transactions? "))
                if num_transactions < 1:
                    raise ValueError
            except ValueError:
                print("\033[91mInvalid number.\033[0m")
                time.sleep(1)
                sys.exit(1)

            # Clear the terminal after selection
            os.system('clear') if os.name == 'posix' else os.system('cls')
            print_intro()
            print(f"\033[94mRunning {num_transactions} rounds of transactions for {multi_network}...\033[0m")
            time.sleep(2)

            web3 = Web3(Web3.HTTPProvider(networks[multi_network]['rpc_url']))

            completed_transactions = 0

            try:
                nonce = web3.eth.get_transaction_count(account.address)
                for _ in range(num_transactions):
                    for bridge in bridges[multi_network]:
                        try:
                            data = Data_HEX[bridge]
                            tx_hash, value_sent = send_bridge_transaction(web3, account, data, multi_network, nonce)
                            nonce += 1  # Increment nonce locally

                            if tx_hash:
                                print(f"\033[92mTx Hash: {tx_hash}\nBridge: {bridge} | Amount: {value_sent} ETH | Total Tx: {completed_transactions + 1}\033[0m")
                                save_tx_hash(tx_hash, multi_network, bridge)
                                completed_transactions += 1
                            else:
                                print(f"\033[91mFailed to send transaction for {bridge}.\033[0m")

                            time.sleep(random.uniform(4, 6))  # Delay antara 4-6 detik
                        except KeyboardInterrupt:
                            print("\n\033[93mBot Stop\033[0m")
                            sys.exit(0)
                        except Exception as e:
                            print(f"\033[91mError processing transaction for {bridge}: {e}\033[0m")

                print(f"\n\n\033[92mAll Multi Bridge Transactions Complete: Tx {completed_transactions}\033[0m")
                sys.exit(0)
            except KeyboardInterrupt:
                print("\n\033[93mBot Stop\033[0m")
                sys.exit(0)

        elif selected_network == "Run All Network":
            run_all_network(account)

        else:
            print(f"\n=== Select Bridge for {selected_network} ===")
            bridges = {
                'Arbitrum Sepolia': ["ARB - OP SEPOLIA", "ARB - BASE", "ARB - BLAST"],
                'OP Sepolia': ["OP - ARB", "OP - BASE", "OP - BLAST"],
                'Base Sepolia': ["BASE - ARB", "BASE - OP", "BASE - BLAST"],
                'Blast Sepolia': ["BLAST - ARB", "BLAST - OP", "BLAST - BASE"]
            }

            for i, bridge in enumerate(bridges[selected_network], start=1):
                print(f"{i}. {bridge}")
            print("========================================\n")

            bridge_choice = input(f"Enter bridge choice (1-{len(bridges[selected_network])}): ")
            if not bridge_choice.isdigit() or not (1 <= int(bridge_choice) <= len(bridges[selected_network])):
                print("\033[91mInvalid choice.\033[0m")
                time.sleep(1)
                sys.exit(1)

            selected_bridge = bridges[selected_network][int(bridge_choice) - 1]

            try:
                num_transactions = int(input("How many times do you want to swap or bridge? "))
                if num_transactions < 1:
                    raise ValueError
            except ValueError:
                print("\033[91mInvalid number.\033[0m")
                time.sleep(1)
                sys.exit(1)

            # Clear the terminal after selection
            os.system('clear') if os.name == 'posix' else os.system('cls')
            print_intro()
            print(f"\033[94mSending {num_transactions} transactions from {selected_network} to {selected_bridge}...\033[0m\n")
            time.sleep(2)

            web3 = Web3(Web3.HTTPProvider(networks[selected_network]['rpc_url']))

            completed_transactions = 0

            try:
                nonce = web3.eth.get_transaction_count(account.address)
                for transaction_number in range(1, num_transactions + 1):
                    try:
                        data = Data_HEX[selected_bridge]
                        tx_hash, value_sent = send_bridge_transaction(web3, account, data, selected_network, nonce)
                        nonce += 1  # Increment nonce locally

                        if tx_hash:
                            print(f"\033[92mTx Hash: {tx_hash}\nBridge: {selected_bridge} | Amount: {value_sent} ETH | Total Tx: {transaction_number}\033[0m")
                            save_tx_hash(tx_hash, selected_network, selected_bridge)
                            completed_transactions += 1
                        else:
                            print(f"\033[91mFailed to send transaction {transaction_number}.\033[0m")

                        time.sleep(random.uniform(4, 6))  # Delay antara 4-6 detik
                    except KeyboardInterrupt:
                        print("\n\033[93mBot Stop\033[0m")
                        sys.exit(0)
                    except Exception as e:
                        print(f"\033[91mError processing transaction {transaction_number}: {e}\033[0m")

                print(f"\n\n\033[92mAll Transactions Complete: Tx {completed_transactions}\033[0m")
                sys.exit(0)
            except KeyboardInterrupt:
                print("\n\033[93mBot Stop\033[0m")
                sys.exit(0)

    except KeyboardInterrupt:
        print("\n\033[93mBot Stop\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()
