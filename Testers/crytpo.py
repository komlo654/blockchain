import sys
from datetime import datetime
import hashlib
import rsa


class User:
    def __init__(self, name, balance=None):
        self.name = name
        self.balance = balance if balance is not None else 100
        self.pubkey, self.__privkey = rsa.newkeys(512)

    def send(self, receiver, amount):
        if self.balance >= amount:
            tr = Transaction(self, receiver, amount)
            sign = rsa.sign(str(tr).encode(), self.__privkey, "SHA-256")
            return {"transaction": tr, "sign": sign}
        else:
            sys.exit(f"{self.name} has not enough money.")


class Transaction:
    def __init__(self, sender, receiver, amount):
        self.timestamp = datetime.now()
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __str__(self):
        return f"{self.timestamp}\n{self.sender.name} send {self.amount} coin to {self.receiver.name}\nSender's public key:\n{self.sender.pubkey.save_pkcs1().decode('UTF-8')}"

    def executing(self):
        self.sender.balance -= self.amount
        self.receiver.balance += self.amount

    def verification(self, signature):
        if rsa.verify(str(self).encode(), signature, self.sender.pubkey):
            return True
        return False

    def get_hash(self):
        hash_ = hashlib.sha256(str(self).encode())
        return hash_.digest()


class Block:
    def __init__(self, block_number, prev_hash, hash_of_transactions):
        self.block_number = block_number
        self.prev_hash = prev_hash
        self.hash_of_transactions = hash_of_transactions
        self.nonce = 0

    def __str__(self):
        return f"Block number: {self.block_number}\nNonce: {self.nonce}\nHash of transactions: {self.hash_of_transactions}\nHash of previous block: {self.prev_hash}"

    def mining(self, difficulty):
        while self.get_hash()[0:difficulty] != '0' * difficulty:
            self.nonce += 1
        return self.get_hash()

    def get_hash(self):
        hash_ = hashlib.sha256(str(self).encode())
        return hash_.hexdigest()


class Blockchain:
    def __init__(self, difficulty):
        self.blocks = []
        self.difficulty = difficulty
        self.current_block_number = 0
        genesis = Block(self.current_block_number + 1, '0' * 64, '0' * 64)
        genesis.mining(self.difficulty)
        self.append_block(genesis)

    def show_chain(self):
        for block in self.blocks:
            print(block, "\nHash of current block: ", block.get_hash(), end="\n---------\n")

    def get_last_block(self):
        return self.blocks[self.current_block_number - 1]

    def append_block(self, block):
        self.blocks.append(block)
        self.current_block_number += 1


class ValidTransactions:
    def __init__(self, hashes):
        self.hashes = hashes
        self.valid_transactions = []

    def validator(self):
        for transaction in self.hashes:
            if transaction["transaction"].verification(transaction["sign"]):
                self.valid_transactions.append(transaction["transaction"].get_hash())
                transaction["transaction"].executing()
            else:
                return "This is an invalid transaction: ", transaction["transaction"]

        return self.valid_transactions


class MerkleTree:
    def __init__(self):
        pass

    def get_root(self, hashes):
        while len(hashes) != 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])

            merkle_hashes = []
            for index in range(0, len(hashes) - 1, 2):
                hash_ = hashlib.sha256(hashes[index] + hashes[index + 1])
                merkle_hashes.append(hash_.digest())
            hashes = merkle_hashes

        return hashes[0].hex()


feri = User("Feri")
peti = User("Peti", 150)
miklos = User("Miklós")
eniko = User("Eniko", 10)
users = [feri, peti, miklos, eniko]

print("Users balance before send coin\n------------------------------------------------------")
for user in users:
    print(f"Username: {user.name}, balance: {user.balance}")
print("------------------------------------------------------")

tr1 = feri.send(peti, 10)
tr2 = feri.send(miklos, 30)
tr3 = miklos.send(eniko, 30)
tr4 = eniko.send(peti, 5)
transactions = [tr1, tr2, tr3, tr4]

print(transactions[0]["transaction"], "\n------------------------------------------------------")

merkle_tree = MerkleTree()
hashes = ValidTransactions(transactions).validator()
hash_of_transactions = merkle_tree.get_root(hashes)
block_chain = Blockchain(4)

# number 2
block1 = Block(block_chain.current_block_number + 1, block_chain.get_last_block().get_hash(), hash_of_transactions)
block1.mining(block_chain.difficulty)
block_chain.append_block(block1)

# number 3
block2 = Block(block_chain.current_block_number + 1, block_chain.get_last_block().get_hash(), hash_of_transactions)
block2.mining(block_chain.difficulty)
block_chain.append_block(block2)

# number 4
block3 = Block(block_chain.current_block_number + 1, block_chain.get_last_block().get_hash(), hash_of_transactions)
block3.mining(block_chain.difficulty)
block_chain.append_block(block3)

# blockchain
block_chain.show_chain()

print("Users balance after sent coin\n------------------------------------------------------")
for user in users:
    print(f"Username: {user.name}, balance: {user.balance}")



