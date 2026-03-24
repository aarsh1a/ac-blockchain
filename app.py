from flask import Flask, jsonify, request, render_template
from blockchain import Blockchain

app = Flask(__name__)

# Initialize blockchain and seed with demo transactions
bc = Blockchain()
for tx in [
    "Alice > Bob : 50 BTC",
    "Bob > Carol : 20 BTC",
    "Carol > Dave : 15 BTC",
]:
    bc.add_block(tx)

print("[*] Blockchain ready. Starting server...")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chain")
def get_chain():
    return jsonify({
        "chain": bc.get_chain_status(),
        "pubkey": bc.get_public_key_str(),
        "difficulty": bc.difficulty
    })


@app.route("/api/add", methods=["POST"])
def add_block():
    data = request.json.get("data", "Anonymous Transaction")
    block = bc.add_block(data)
    return jsonify({"ok": True, "block": block})


@app.route("/api/tamper/<int:idx>", methods=["POST"])
def tamper(idx):
    new_data = request.json.get("data", "TAMPERED DATA")
    bc.tamper_block(idx, new_data)
    return jsonify({"ok": True})


@app.route("/api/remine/<int:idx>", methods=["POST"])
def remine(idx):
    stats = bc.remine_block(idx)
    return jsonify({"ok": True, "stats": stats})


@app.route("/api/difficulty", methods=["POST"])
def set_difficulty():
    d = request.json.get("difficulty", 2)
    actual = bc.set_difficulty(d)
    return jsonify({"ok": True, "difficulty": actual})


@app.route("/api/reset", methods=["POST"])
def reset():
    global bc
    d = bc.difficulty
    bc = Blockchain(difficulty=d)
    for tx in [
        "Alice > Bob : 50 BTC",
        "Bob > Carol : 20 BTC",
        "Carol > Dave : 15 BTC",
    ]:
        bc.add_block(tx)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
