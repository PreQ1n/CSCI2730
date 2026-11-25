from core.block import Block, BlockHeader
from crypto.hashing import make_merkle_root
from threading import Lock

class Chain:
    def __init__(self, difficulty = 3):
        self.blocks = [] #use list to implement will be much easier
        self.balances = {}
        self.difficulty = difficulty
        self.create_genesis()
        self.lock = Lock()

    def create_genesis(self):
        genesis_header = BlockHeader(
            prev_hash = "0" * 64,
            timestamp = 0,
            nonce = 0,
            difficulty = 0,
            miner_id = "genesis",
            merkle = make_merkle_root([])
        )
        genesis_header.hash = genesis_header.compute_hash()
        gensis = Block(genesis_header, [])
        self.blocks.append(gensis)

    def get_last(self) -> Block:
        with self.lock:
            return self.blocks[-1]

    def get_height(self):
        with self.lock:
            return len(self.blocks) - 1

    def get_balance(self, addr : bytes):
        with self.lock:
            return int(self.balances.get(addr, 0))

    def validate_block(self, block : Block, prev_block : Block):
        with self.lock:
            #check prev block hash
            if block.header.prev_hash != prev_block.header.hash:
                return False
            #check merkle root (transaction)
            if block.header.merkle != Block.compute_merkle_root(block.transactions):
                return False
            #check signature
            for transaction in block.transactions:
                if not transaction.verify_transaction():
                    return False

            return True

    def add_block(self, block : Block):
        if not self.validate_block(block, self.get_last()):
            return False

        for transaction in block.transactions:
            if transaction.type == "transfer":
                self.balances[transaction.from_addr] = self.get_balance(transaction.from_addr) - int(transaction.amount)
                self.balances[transaction.to_addr] = self.get_balance(transaction.to_addr) + int(transaction.amount)

        self.blocks.append(block)
        return True

    def replace_if_longer(self, other_blocks: list):
        if len(other_blocks) <= len(self.blocks):
            return 

        new_chain = Chain(self.difficulty)
        new_chain.blocks = [self.blocks[0]]
        new_chain.balances = {}
        for block in other_blocks[1:]:
            if not new_chain.add_block(block):
                return

        self.blocks = new_chain.blocks
        self.balances = new_chain.balances

        
