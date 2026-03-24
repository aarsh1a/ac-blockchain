import hashlib
import json
import time
import rsa


class Block:
    def __init__(self, index, data, prev_hash, timestamp=None):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.data = data
        self.prev_hash = prev_hash
        self.nonce = 0
        self.hash = self._compute_hash()
        self.signature = None
        self.mine_time_ms = None
        self.mine_iterations = None

    def _compute_hash(self):
        content = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "prev_hash": self.prev_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def mine(self, difficulty):
        """Proof of Work: find nonce so hash starts with `difficulty` zeros."""
        target = "0" * difficulty
        self.nonce = 0
        self.hash = self._compute_hash()
        start = time.perf_counter()
        iterations = 1
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self._compute_hash()
            iterations += 1
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        self.mine_time_ms = elapsed_ms
        self.mine_iterations = iterations
        return {"time_ms": elapsed_ms, "iterations": iterations, "nonce": self.nonce}

    def sign(self, private_key):
        """Sign the block's hash with RSA private key."""
        try:
            sig_bytes = rsa.sign(self.hash.encode(), private_key, "SHA-1")
            self.signature = sig_bytes.hex()
        except Exception:
            self.signature = None

    def verify_signature(self, public_key):
        """Verify RSA signature against the recomputed hash of current data.
        
        We verify against _compute_hash() — not self.hash — so that if an
        attacker tampers with the data without updating the stored hash, the
        recomputed hash will differ from what was signed and the check fails.
        """
        if not self.signature:
            return False
        try:
            current_hash = self._compute_hash()
            rsa.verify(current_hash.encode(), bytes.fromhex(self.signature), public_key)
            return True
        except Exception:
            return False

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": round(self.timestamp, 2),
            "data": self.data,
            "prev_hash": self.prev_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "signature": self.signature,
            "mine_time_ms": self.mine_time_ms,
            "mine_iterations": self.mine_iterations
        }


class Blockchain:
    def __init__(self, difficulty=2):
        print("[*] Generating RSA-512 key pair...")
        self.public_key, self.private_key = rsa.newkeys(512)
        print("[*] Keys ready. Building genesis block...")
        self.difficulty = difficulty
        self.chain = []
        self._add_genesis()

    def _add_genesis(self):
        genesis = Block(0, "Genesis Block", "0" * 64)
        genesis.mine(self.difficulty)
        genesis.sign(self.private_key)
        self.chain.append(genesis)

    def set_difficulty(self, d):
        """Set mining difficulty (number of leading zeros required)."""
        self.difficulty = max(1, min(6, int(d)))
        return self.difficulty

    def add_block(self, data):
        """Mine a new block and append to chain."""
        new_block = Block(len(self.chain), data, self.chain[-1].hash)
        stats = new_block.mine(self.difficulty)
        new_block.sign(self.private_key)
        self.chain.append(new_block)
        result = new_block.to_dict()
        result["mine_stats"] = stats
        return result

    def tamper_block(self, index, new_data):
        """Tamper with a block's data WITHOUT recomputing hash (simulates attack)."""
        if 1 <= index < len(self.chain):
            self.chain[index].data = new_data
            # Intentionally NOT recomputing hash — this breaks integrity

    def remine_block(self, index):
        """Re-mine a single block (attacker's attempt to fix tampering)."""
        if 1 <= index < len(self.chain):
            block = self.chain[index]
            block.prev_hash = self.chain[index - 1].hash
            stats = block.mine(self.difficulty)
            block.sign(self.private_key)
            # Note: subsequent blocks are NOT updated — cascade failure remains
            return stats
        return None

    def get_chain_status(self):
        """Return full chain with per-block validity analysis."""
        result = []
        for i, block in enumerate(self.chain):
            hash_ok = (block.hash == block._compute_hash())
            link_ok = (i == 0) or (block.prev_hash == self.chain[i - 1].hash)
            sig_ok = block.verify_signature(self.public_key)
            entry = block.to_dict()
            entry.update(
                hash_ok=hash_ok,
                link_ok=link_ok,
                sig_ok=sig_ok,
                valid=(hash_ok and link_ok and sig_ok)
            )
            result.append(entry)
        return result

    def get_public_key_str(self):
        return self.public_key.save_pkcs1().decode()
