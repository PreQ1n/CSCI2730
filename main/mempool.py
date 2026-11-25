#for temporarily storing the transaction 

from core.transaction import Transaction
from threading import Lock

class Mempool:
    def __init__(self):
        self.pending = {}
        self.lock = Lock()

    def add(self, transaction : Transaction):
        with self.lock:
        #verify validity
            if not transaction.verify_transaction():
                return False
            #not adding repeat transaction
            hashing = transaction.transaction_hash()
            if hashing in self.pending:
                return False
            
            self.pending[hashing] = transaction

            return True 

    def remove(self, transactions : list[bytes]):
        with self.lock:
            for hashing in transactions:
                self.pending.pop(hashing, None)

    def get(self, chain, max_per_time=10):
        with self.lock:
            selected = []
            temp_balances = dict(chain.balances) #copying out the main chain balances for verification

            for hashing, transaction in self.pending.items():
                if transaction.type == "transfer":
                    sender_bal = int(temp_balances.get(transaction.from_addr, 0))
                    if int(sender_bal) < int(transaction.amount):
                        continue

                    temp_balances[transaction.from_addr] = int(temp_balances.get(transaction.from_addr, 0)) - int(transaction.amount)
                    temp_balances[transaction.to_addr] = int(temp_balances.get(transaction.to_addr, 0)) + int(transaction.amount)

                selected.append(transaction)

                if len(selected) > max_per_time:
                    break
                
            return selected 

    def size(self):
        with self.lock:
            return len(self.pending)


    

        
