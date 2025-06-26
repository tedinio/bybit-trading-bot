from flask import Flask, request, jsonify
import json
import requests

# Bybit REST API
import hmac
import hashlib
import time

# Load API credentials
with open("config.json") as f:
    config = json.load(f)

API_KEY = config["api_key"]
API_SECRET = config["api_secret"]

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No JSON received"}), 400

    signal = data.get("signal")
    symbol = data.get("symbol", "ETHUSDT")

    if signal not in ["buy", "sell"]:
        return jsonify({"message": "Invalid signal"}), 400

    print(f"Received {signal} signal for {symbol}")

    order_side = "Buy" if signal == "buy" else "Sell"

    timestamp = int(time.time() * 1000)
    endpoint = "https://api.bybit.com/v5/order/create"

    payload = {
        "category": "linear",
        "symbol": symbol,
        "side": order_side,
        "orderType": "Market",
        "qty": "0.01",  # Δοκιμαστική ποσότητα
        "timeInForce": "GoodTillCancel",
        "timestamp": str(timestamp),
        "apiKey": API_KEY
    }

    # Υπογραφή
    param_str = "&".join(f"{k}={v}" for k, v in sorted(payload.items()))
    signature = hmac.new(
        API_SECRET.encode("utf-8"),
        param_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    payload["sign"] = signature

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(endpoint, json=payload, headers=headers)
    print("Bybit API response:", response.json())

    return jsonify({"message": f"Trade executed: {signal} on {symbol}"}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
