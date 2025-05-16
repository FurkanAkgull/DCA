import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

config = {
    "symbol": ["DOGEUSDT"],
    "usdt_to_spend": 10,
    "profit_target": 1.01,
    "price": 0.224500
}

@app.route("/get_config", methods=["GET"])
def get_config():
    return jsonify(config)

@app.route('/update_config', methods=['POST'])
def update_config():
    data = request.json
    config.update(data)
    return jsonify({"status": "updated", "new_config": config})

@app.route('/get_price', methods=['GET'])
def get_price():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "symbol param is required"}), 400
    
    # Burada sadece config'teki price değerini dönüyoruz.
    # İstersen symbol kontrolü yapabilirsin (şimdilik sadece 1 symbol var).
    if symbol not in config["symbol"]:
        return jsonify({"error": f"Symbol {symbol} not found in config"}), 404
    
    return jsonify({"symbol": symbol, "price": config["price"]})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
