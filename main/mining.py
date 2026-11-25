from core.block import Block, BlockHeader
import time
import random

def mine_block(chain, mempool, miner_id):
    transactions = mempool.get(chain)

    if not transactions:
        return None

    merkle = Block.compute_merkle_root(transactions)
    header = BlockHeader(
        prev_hash = chain.get_last().block_hash(),
        timestamp = int(time.time()),
        nonce = random.randint(0, 2**16),
        difficulty = chain.difficulty,
        miner_id = miner_id,
        merkle = merkle
    )

    target = "0" * chain.difficulty #it will be a simple implement of the miner question
    while not header.compute_hash().startswith(target):
        header.nonce += 1

    header.hash = header.compute_hash()
    return Block(header, transactions)