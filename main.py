from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import time
import json
import os

app = Flask(__name__)

# Φόρτωση ρυθμίσεων
with open("config.json") as f:
    config = json.load(f)

API_KEY = config["api_key"]
API_SECRET = config["api_secret"]
BASE_URL = "https://api.bybit.com"

def create_order(symbol, side, qty, trailing_stop):
    endpoint = "/v5/order/create"
    url = BASE_URL + endpoint
    timestamp = str(int(time.time() * 1000))

    body = {
        "category": "linear",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": qty,
        "timeInForce": "GoodTillCancel",
        "reduceOnly": False,
        "triggerDirection": 1,
        "trailingStop": trailing_stop
    }

    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": "5000",
        "Content-Type": "application/json"
    }

    # Υπογραφή
    param_str = timestamp + API_KEY + "5000" + json.dumps(body)
    sign = hmac.new(API_SECRET.encode("utf-8"), param_str.encode("utf-8"), hashlib.sha256).hexdigest()
    headers["X-BAPI-SIGN"] = sign

    response = requests.post(url, headers=headers, json=body)
    return response.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Received Alert:", data)

    symbol = data.get("symbol", "ETHUSDT")
    side = "Buy" if data["signal"] == "buy" else "Sell"
    qty = 0.01  # Παράδειγμα ποσότητας
    trailing_stop = "2"  # Απόσταση σε $

    result = create_order(symbol, side, qty, trailing_stop)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)