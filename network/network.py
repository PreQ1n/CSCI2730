from network.connect import Connect
from core.block import Block
import threading
import requests
import socket
import time

class Network:
    def __init__(self, my_ip, my_port, bootnode, node):
        self.bootnode = bootnode
        self.peers = {} # {"ip:port" : Connect}
        self.transaction = set()
        self.block = set()
        self.my_ip = my_ip
        self.my_port = my_port
        self.node = node
        self.lock = threading.Lock() 

    def start(self):
        nodes = self.register() #Get all peers

        for node in nodes:
            self.add_node(node["ip"], node["port"])

        threading.Thread(target = self.listening, daemon = True).start() #it will start listening to other peer
        threading.Thread(target = self.reporting_to_bootnode, daemon = True).start()

    def register(self): #Register and Get the peers list from bootnode
        try:
            request = requests.post(f"{self.bootnode}/register", json = {"ip" : self.my_ip, "port" : self.my_port}, timeout = 5)
            return request.json().get("nodes", [])
        except Exception as e:
            print(f"Register Failed, {e}")
            return []
        
    def add_node(self, ip, port):
        print(f"[add_node] connecting to {ip}:{port}") 
        if ip == self.my_ip and port == self.my_port:
            return

        with self.lock:
            key = f"{ip}:{port}"
            if key in self.peers:
                return 

            connection = Connect(ip, port, self.on_message)

        if connection.connect():
            self.peers[key] = connection
            connection.send({"type" : "handshake", "ip" : self.my_ip, "port" : self.my_port})
        else:
            with self.lock:
                self.peers.pop(key, None)

    def listening(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as receiving_node:
            receiving_node.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            receiving_node.bind(("0.0.0.0", self.my_port))
            receiving_node.listen(10)
            print(f"Listening on {self.my_port}")

            while True:
                conn, addr = receiving_node.accept()
                print(f"[accept] incoming from {addr}") 
                connection = Connect(addr[0], 0, self.on_message)
                connection.accept_connection(conn)

    def reporting_to_bootnode(self):
        while True:
            time.sleep(10)
            try:
                request = requests.post(f"{self.bootnode}/report", json = {"ip" : self.my_ip, "port" : self.my_port}, timeout = 5)
            except Exception as e:
                print(f"Report Failed, {e}")

    def on_message(self, message, connection):
        msg_type = message["type"]

        if msg_type == "handshake": 
            print(f"[handshake] from {message['ip']}:{message['port']}")
            key = f"{message['ip']}:{message['port']}"
            self.peers[key] = connection
            connection.ip = message["ip"]
            connection.port = message["port"] 

            #normally the side receive handshake is the older side, so we can just send the chain to the new side and sync the chain
            chain_data = [block.to_dict() for block in self.node.chain.blocks]
            print(f"[handshake] sending chain with {len(chain_data)} blocks to {key}") 
            connection.send({"type" : "chain", "data" : chain_data})

        elif msg_type == "transaction":
            hashing = message["hash"]

            with self.lock:
                if hashing in self.transaction:
                    return 
                self.transaction.add(hashing)

            self.node.receive_transaction(message["data"])
            self.broadcast_all(message)

        elif msg_type == "block":
            hashing = message["hash"]

            with self.lock:
                if hashing in self.block:
                    return 
                self.block.add(hashing)

            self.node.receive_block(message["data"])
            self.broadcast_all(message)

        elif msg_type == "chain":
            blocks = [Block.from_dict(block) for block in message["data"]]
            self.node.chain.replace_if_longer(blocks)

    def broadcast_transaction(self, transaction):
        hashing = transaction.transaction_hash()

        with self.lock:
            if hashing in self.transaction:
                return
            self.transaction.add(hashing)

        message = {"type" : "transaction", "hash" : hashing, "data" : transaction.to_dict()}
        self.broadcast_all(message)

    def broadcast_block(self, block):
        hashing = block.header.hash

        with self.lock:
            if hashing in self.block:
                return 
            self.block.add(hashing)

        message = {"type" : "block", "hash" : hashing, "data" : block.to_dict()}
        self.broadcast_all(message)

    def broadcast_all(self, message):
        with self.lock:
            peers = list(self.peers.items())

        dead = []
        for key, peer in peers:
            if not peer.send(message):
                dead.append(key)
        if dead:
            with self.lock:
                for key in dead:
                    self.peers.pop(key, None)

    def shutdown(self):
        with self.lock:
            peers = list(self.peers.values())
            self.peers.clear()
        for connection in peers:
            connection.close()




    

    





