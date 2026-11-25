from main.mempool import Mempool
from main.mining import mine_block
from core.chain import Chain
from core.transaction import Transaction
from core.block import Block

import time
import threading

class Node:
    def __init__(self, address):
        self.mempool = Mempool()
        self.chain = Chain()
        self.address = address
        self.running = False
        self.network = None

    def set_network(self, network):
        self.network = network

    def start(self):
        self.running = True
        threading.Thread(target = self.mining, daemon = True).start()

    #it will keep mining when the node is started, so when a transaction is arrived, it can always in response
    def mining(self):
        while self.running:
            if self.mempool.size() == 0:
                time.sleep(1)
                continue

            block = mine_block(self.chain, self.mempool, self.address)

            if self.chain.add_block(block):
                hashing = []
                for transaction in block.transactions:
                    hashing.append(transaction.transaction_hash())

                self.mempool.remove(hashing) #remove those selected transaction
                self.broadcast_block(block)
            else:
                continue

    def broadcast_transaction(self, transaction):
        if self.network:
            self.network.broadcast_transaction(transaction)

    def broadcast_block(self, block):
        if self.network:
            self.network.broadcast_block(block)

    def submit_transaction(self, transaction):
        if self.mempool.add(transaction):
            self.broadcast_transaction(transaction)

    def receive_transaction(self, message):
        transaction = Transaction.from_dict(message)
        self.mempool.add(transaction)

    def receive_block(self, message):
        block = Block.from_dict(message)
        if self.chain.add_block(block):
            hashes = [transaction.transaction_hash() for transaction in block.transactions]
            self.mempool.remove(hashes)


    