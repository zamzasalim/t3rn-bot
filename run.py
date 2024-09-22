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
    terminal_width = os.get_terminal_size().columns
    lines = text.splitlines()
    centered_lines = [line.center(terminal_width) for line in lines]
    return "\n".join(centered_lines)

intro_text = """
                ==============================================
                              AIRDROP ASC
                 ==============================================
            Credit By       : Airdrop ASC
            Telegram Channel: @airdropasc
                 Telegram Group  : @autosultan_group
                 ==============================================
"""

def print_intro():
    os.system('clear') if os.name == 'posix' else os.system('cls')
    print("\033[96m" + center_text(intro_text) + "\033[0m")
    print("\n\n")

def get_current_gas_price(web3):
    gas_price_wei = web3.eth.gas_price
    gas_price_gwei = web3.from_wei(gas_price_wei, 'gwei')
    return gas_price_gwei

def send_bridge_transaction(web3, account, data, network_name, nonce):
    value_in_ether = float(VALUE_ETH)
    value_in_wei = web3.to_wei(value_in_ether, 'ether')

    try:
        gas_estimate = web3.eth.estimate_gas({
            'to': networks[network_name]['contract_address'],
            'from': account.address,
            'data': data,
            'value': value_in_wei
        })
        gas_limit = gas_estimate + GAS_LIMIT_ADJUSTMENT
    except Exception as e:
        print(f"Error estimating gas: {e}")
        return None, None

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

    try:
        signed_txn = web3.eth.account.sign_transaction(transaction, account.key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return web3.to_hex(tx_hash), value_in_ether
    except ValueError as e:
        print(f"Error sending transaction: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error sending transaction: {e}")
        return None, None

def validate_private_key(private_key):
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    if len(private_key) != 66:
        return False
    try:
        int(private_key[2:], 16)  # Check if it's a valid hex string
    except ValueError:
        return False
    return True

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

def main():
    print_intro()
    print("Select network:")
    print("1. ARB (Arbitrum Sepolia)")
    print("2. OP (Optimism Sepolia)")
    print("3. BASE (Base Sepolia)")
    print("4. BLAST (Blast Sepolia)")
    print("5. Multi Bridge (Run all transactions for selected network)")

    network_choice = input("Network choice (1-5): ")
    network_dict = {
        '1': 'Arbitrum Sepolia',
        '2': 'OP Sepolia',
        '3': 'Base Sepolia',
        '4': 'Blast Sepolia',
        '5': 'Multi Bridge'
    }
    if network_choice not in network_dict:
        print("Invalid choice.")
        sys.exit(1)

    selected_network = network_dict[network_choice]

    # Clear the terminal after selection
    os.system('clear') if os.name == 'posix' else os.system('cls')
    print_intro()

    if selected_network == "Multi Bridge":
        print("You have selected Multi Bridge mode. Running transactions simultaneously for selected network.")
        bridges = {
            'Arbitrum Sepolia': ["ARB - OP SEPOLIA", "ARB - BASE", "ARB - BLAST"],
            'OP Sepolia': ["OP - ARB", "OP - BASE", "OP - BLAST"],
            'Base Sepolia': ["BASE - ARB", "BASE - OP", "BASE - BLAST"],
            'Blast Sepolia': ["BLAST - ARB", "BLAST - OP", "BLAST - BASE"]
        }

        print("Select network for Multi Bridge:")
        for i, (key, value) in enumerate(network_dict.items(), start=1):
            if key != '5':  # Exclude Multi Bridge option
                print(f"{i}. {value}")

        multi_bridge_choice = input("Network choice for Multi Bridge (1-4): ")
        if multi_bridge_choice not in ['1', '2', '3', '4']:
            print("Invalid choice.")
            sys.exit(1)

        multi_network = network_dict[multi_bridge_choice]
        try:
            num_transactions = int(input("How many rounds do you want to repeat the transactions? "))
        except ValueError:
            print("Invalid number.")
            sys.exit(1)

        # Clear the terminal after selection
        os.system('clear') if os.name == 'posix' else os.system('cls')
        print_intro()
        print(f"Running {num_transactions} rounds of transactions for {multi_network}...")

        web3 = Web3(Web3.HTTPProvider(networks[multi_network]['rpc_url']))
        private_key = private_keys[0]
        if not validate_private_key(private_key):
            print("Invalid private key format.")
            sys.exit(1)

        account = Account.from_key(private_key)
        completed_transactions = 0

        for _ in range(num_transactions):
            for bridge in bridges[multi_network]:
                try:
                    nonce = web3.eth.get_transaction_count(account.address)
                    data = Data_HEX[bridge]
                    tx_hash, value_sent = send_bridge_transaction(web3, account, data, multi_network, nonce)

                    if tx_hash:
                        print(f"\033[92mTx Hash: {tx_hash}\nBridge: {bridge} | Amount: {value_sent} ETH | Total Tx: {completed_transactions + 1}\033[0m")
                        save_tx_hash(tx_hash, multi_network, bridge)
                        completed_transactions += 1
                    else:
                        print(f"Failed to send transaction for {bridge}.")
                    
                    time.sleep(random.uniform(5, 10))  # Random delay between transactions
                except Exception as e:
                    print(f"Error processing transaction for {bridge}: {e}")

        print(f"\n\n\033[92mAll Multi Bridge Transactions complete: {completed_transactions}\033[0m")

    else:
        print(f"Select bridge for {selected_network}:")
        bridges = {
            'Arbitrum Sepolia': ["ARB - OP SEPOLIA", "ARB - BASE", "ARB - BLAST"],
            'OP Sepolia': ["OP - ARB", "OP - BASE", "OP - BLAST"],
            'Base Sepolia': ["BASE - ARB", "BASE - OP", "BASE - BLAST"],
            'Blast Sepolia': ["BLAST - ARB", "BLAST - OP", "BLAST - BASE"]
        }
        
        for i, bridge in enumerate(bridges[selected_network], start=1):
            print(f"{i}. {bridge}")

        bridge_choice = input("Enter bridge choice: ")
        if not bridge_choice.isdigit() or int(bridge_choice) not in range(1, len(bridges[selected_network]) + 1):
            print("Invalid choice.")
            sys.exit(1)

        selected_bridge = bridges[selected_network][int(bridge_choice) - 1]

        try:
            num_transactions = int(input("How many times do you want to swap or bridge? "))
        except ValueError:
            print("Invalid number.")
            sys.exit(1)

        # Clear the terminal after selection
        os.system('clear') if os.name == 'posix' else os.system('cls')
        print_intro()
        print(f"\nSending {num_transactions} transactions from {selected_network} to {selected_bridge}...\n")

        web3 = Web3(Web3.HTTPProvider(networks[selected_network]['rpc_url']))
        private_key = private_keys[0]
        if not validate_private_key(private_key):
            print("Invalid private key format.")
            sys.exit(1)

        account = Account.from_key(private_key)
        completed_transactions = 0

        for transaction_number in range(1, num_transactions + 1):
            try:
                nonce = web3.eth.get_transaction_count(account.address)
                data = Data_HEX[selected_bridge]
                tx_hash, value_sent = send_bridge_transaction(web3, account, data, selected_network, nonce)

                if tx_hash:
                    print(f"\033[92mTx Hash: {tx_hash}\nBridge: {selected_bridge} | Amount: {value_sent} ETH | Total Tx: {transaction_number}\033[0m")
                    save_tx_hash(tx_hash, selected_network, selected_bridge)
                    completed_transactions += 1
                else:
                    print(f"Failed to send transaction {transaction_number}.")
                
                time.sleep(random.uniform(8, 10))  # Random delay between transactions
            except Exception as e:
                print(f"Error processing transaction {transaction_number}: {e}")

        print(f"\n\n\033[92mAll Transactions complete: {completed_transactions}\033[0m")

if __name__ == "__main__":
    main()
