from qcrypto import FalconSig

class FalconKeyPair:
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key

def generate_keypair():
    sig = FalconSig("Falcon-512")
    keys = sig.generate_keypair()
    return FalconKeyPair(keys.public_key, keys.secret_key)

def sign(message: bytes, private_key: bytes):
    sig = FalconSig("Falcon-512")
    return sig.sign(private_key, message)

def verify(public_key: bytes, signature: bytes, message: bytes):
    sig = FalconSig("Falcon-512")
    return sig.verify(public_key, message, signature)



    