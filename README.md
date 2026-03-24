# cryptochain - live blockchain visualizer

## applied cryptography project | SHA-256 + RSA-512 + proof-of-work

it shows how the core crypto behind blockchains actually works with a ui where you can mine blocks, mess with the data, and watch the chain break.

## stack
- backend: python, flask
- crypto: hashlib (sha-256), rsa (rsa-512)
- frontend: vanilla html, css, js

## what it shows
- **proof of work**: you can change the mining difficulty to see how long it takes to find a valid nonce (`blockchain.py` -> `mine()`).
- **immutability (sha-256)**: each block stores the hash of the previous one. if you tamper with a block's data, its hash changes and the link breaks (`_compute_hash`).
- **authenticity (rsa-512)**: every new session generates an rsa keypair. blocks are signed with the private key. if you edit the block, the signature fails since the recomputed hash won't match (`sign()` and `verify_signature()`).
- **cascade failure**: if you try to remine a tampered block to fix its hash, it just breaks the next block's `prev_hash` pointer. you'd have to remine the entire chain faster than the rest of the network to get away with it.

## how to run

1. clone the repo
```bash
git clone https://github.com/aarsh1a/ac-blockchain.git
cd ac-blockchain
```

2. install stuff
```bash
pip install flask rsa
```

3. run it
```bash
python app.py
```
then open `http://127.0.0.1:5000`
