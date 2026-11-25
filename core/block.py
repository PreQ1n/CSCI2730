from crypto.hashing import make_merkle_root, sha256_hex
from core.transaction import Transaction
import json

class BlockHeader:
    def __init__(self, prev_hash, timestamp, nonce, difficulty, miner_id, merkle):
        self.prev_hash = prev_hash
        self.timestamp = timestamp
        self.nonce = nonce
        self.difficulty = difficulty
        self.miner_id = miner_id
        self.merkle = merkle
        self.hash = None

    def header_bytes(self) -> bytes:
        d = {
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "miner_id": self.miner_id,
            "merkle": self.merkle.hex(),  
        }
        return json.dumps(d, sort_keys=True).encode()

    def compute_hash(self) -> str:
        return sha256_hex(self.header_bytes())

    #for broadcast, has hash
    def to_dict(self) -> dict:
        return {
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "miner_id": self.miner_id,
            "merkle": self.merkle.hex(),
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, msg: dict):
        temp = cls(
            prev_hash = msg["prev_hash"],
            timestamp = msg["timestamp"],
            nonce = msg["nonce"],
            difficulty = msg["difficulty"],
            miner_id = msg["miner_id"],
            merkle = bytes.fromhex(msg["merkle"])
        )
        temp.hash = msg["hash"]

        return temp
    
class Block:
    def __init__(self, header :BlockHeader, transactions :list[Transaction]):
        self.header = header
        self.transactions = transactions

    @staticmethod
    def compute_merkle_root(transactions: list[Transaction]):
        transactions_hash_list = []
        for transaction in transactions:
            transactions_hash_list.append(bytes.fromhex(transaction.transaction_hash()))

        return make_merkle_root(transactions_hash_list)

    def block_hash(self):
        return self.header.hash

    def to_dict(self):
        return {
            "header" : self.header.to_dict(),
            "transactions" : [transaction.to_dict() for transaction in self.transactions]
        }

    @classmethod
    def from_dict(cls, msg: dict):
        header = BlockHeader.from_dict(msg["header"])
        transactions = []
        for transaction in msg["transactions"]:
            transactions.append(Transaction.from_dict(transaction))
        return cls(header, transactions)


        