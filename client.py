from crypto.falcons import generate_keypair, FalconKeyPair
from crypto.hashing import make_address
from main.node import Node
from network.network import Network
from core.transaction import Transaction


from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
import json
import requests
import time
import os

def start(my_port, bootnode, my_address, balance):
    my_node = Node(my_address)
    my_node.chain.balances[my_address] = balance
    my_ip = "127.0.0.1"
    # we dont use the public IP in the demo, we will use the localhost
    # my_ip = requests.get("https://api.ipify.org").text 

    my_network = Network(my_ip, my_port, bootnode, my_node)
    my_node.set_network(my_network)
    my_node.network.start()
    my_node.start()

    return my_node

def make_transaction(from_addr, to_addr, amount, my_key):
    transaction = Transaction(from_addr, to_addr, amount, my_key.public_key, 
                              int(time.time()), "transfer")
    transaction.sign_transaction(my_key.private_key)

    return transaction

def read_from_wallet(file):
    if not os.path.exists(file):
        my_key = generate_keypair()
        content = [my_key.public_key.hex(), my_key.private_key.hex()]

        with open(file, "w", encoding = "utf-8") as f:
            json.dump(content, f)
    
    else:
        with open(file, encoding = "utf-8") as f:
            content = json.load(f)
            my_key = FalconKeyPair(bytes.fromhex(content[0]), bytes.fromhex(content[1]))

    my_address = make_address(my_key.public_key)

    return my_key, my_address

#to validate if the wallet is a json file
def json_file(value):
    path = Path(value)
    if path.suffix.lower() != ".json":
        raise ArgumentTypeError(f"'{value}' must be a .json file")
    return path

def print_help():
    print("""
    Command:
        h                                   All Command
        quit, exit                          Exit the client
        address                             Print out your address
        balance                             Show your balance 
        peers                               Show all peers connection
        Transaction <to_addr> <amount>      Transfer <amount> to <to_addr>
    """)

def main():
    parser = ArgumentParser()
    parser.add_argument("--port", required = True)
    parser.add_argument("--bootnode", required = True)
    parser.add_argument("--wallet", type = json_file, required = True)
    parser.add_argument("--balance", default = 0)
    args = parser.parse_args()

    bootnode = "http://" + args.bootnode
    my_key, my_address = read_from_wallet(args.wallet)

    my_node = start(int(args.port), bootnode, my_address, args.balance)

    exiting = False
    while(True):
        if exiting:
            print("Good Bye!")
            break

        command = input(">>").strip()
        if not command:
            continue
        
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == "quit" or cmd == "exit":
            exiting = True

        elif cmd == "address":
            print(my_address)

        elif cmd == "balance":
            print(my_node.chain.balances[my_address])

        elif cmd == "exist":
            n = 1
            for key, item in my_node.chain.balances.items():
                print(f"{n} : {key} --> {item}")
                n += 1

        elif cmd == "transaction":
            if len(parts) < 3:
                print("Wrong Syntax! Should be: transaction <to> <amount>")
                continue
            to_addr = parts[1]
            amount = parts[2]

            balance = my_node.chain.balances[my_address]
            if int(amount) > int(balance):
                print(f"Not enough money! Remaining: {balance}")
                continue

            transaction = make_transaction(my_address, to_addr, amount, my_key)
            my_node.submit_transaction(transaction)
            print(f"{transaction.transaction_hash()[:10]} submmited")

        elif cmd == "peers":
            print(f"Number of Peers: {len(my_node.network.peers)}")
            for key in my_node.network.peers:
                print(key)

        elif cmd == "h":
            print_help()

        else:
            print("Unknown Command! Type h for help")
        

if __name__ == "__main__":
    main()
