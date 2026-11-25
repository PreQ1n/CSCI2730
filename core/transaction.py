from crypto.falcons import sign, verify
from crypto.hashing import sha256_hex, make_address
import json

class Transaction:
    def __init__(self, from_addr, to_addr, amount, public_key, time, type, signature=None):
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.amount = amount
        self.public_key = public_key
        self.time = time
        self.signature = signature
        self.type = type

    def to_dict(self):
        return {
            "from" : self.from_addr,
            "to" : self.to_addr,
            "amount" : self.amount,
            "time" : self.time,
            "type" : self.type,
            "public_key" : self.public_key.hex(),
            "signature" : self.signature.hex()
        }

    @classmethod
    def from_dict(cls, msg: dict):
        return cls(
            from_addr = msg["from"],
            to_addr = msg["to"],
            amount = msg["amount"],
            public_key = bytes.fromhex(msg["public_key"]),
            time = msg["time"],
            type = msg["type"],
            signature = bytes.fromhex(msg["signature"])
        )

    def make_content(self):
        payload = {
            "from" : self.from_addr,
            "to" : self.to_addr,
            "amount" : self.amount,
            "time" : self.time,
            "type" : self.type
        }
        return json.dumps(payload, sort_keys=True).encode()

    # signing transaction
    def sign_transaction(self, private_key):
        self.signature = sign(self.make_content(), private_key)

    def transaction_hash(self): 
        return sha256_hex(self.make_content())

    def verify_transaction(self):
        if make_address(self.public_key) != self.from_addr:
            return False

        if self.signature is None:
            return False

        return verify(self.public_key, self.signature, self.make_content())
        

