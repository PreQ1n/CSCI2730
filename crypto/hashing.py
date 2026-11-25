import hashlib
from Crypto.Hash import RIPEMD160

def sha256(data: bytes):
    return hashlib.sha256(data).digest()

def sha256_hex(data: bytes):
    return hashlib.sha256(data).hexdigest()

def make_address(public_key:bytes):
    sha = hashlib.sha256(public_key).digest() 
    ripemd = RIPEMD160.new(sha).hexdigest() #shorten the address to 20 bytes
    return ripemd

def make_merkle_root(transaction_list: list[bytes]):
    if not transaction_list:
        return b'\x00' * 32

    temp = transaction_list[:]

    while len(temp) > 1:
        if len(temp) % 2 != 0:
            temp.append(temp[-1]) #copy the last element when len(temp) is odd

        temp2 = []
        for i in range(0, len(temp), 2):
            temp2.append(sha256(temp[i] + temp[i + 1]))
        temp = temp2

    return temp[0]