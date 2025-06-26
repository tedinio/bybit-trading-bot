from flask import Flask, request, jsonify
import json
import requests
import hmac
import hashlib
import time

app = Flask(__name__)

# === Βοηθητική συνάρτηση για αποστολή παραγγελίας στην Bybit ===
def send_order(signal, symbol):
    with open("config.json") as f:
        config = json.load(f)

    api_key = config["api_key"]
    api_secret = config["api_secret"]

    timestamp = str(int(time.time() * 1000))
    side = "Buy" if signal == "buy" else "Sell"

    url = "https://api.bybit.com/v5/order/create"

    body = {
        "category": "linear",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": "0.01",
        "timeInForce": "GoodTillCancel"
    }

    body_json = json.dumps(body, separators=(",", ":"))
    recv_window = "5000"

    params = f"{timestamp}{api_key}{recv_window}{body_json}"
    signature = hmac.new(api_secret.encode(), params.encode(), hashlib.sha256).hexdigest()

    headers = {
        "X-BYBIT-API-KEY": api_key,
        "X-BYBIT-SIGN": signature,
        "X-BYBIT-TIMESTAMP": timestamp,
        "X-BYBIT-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=body_json)
    print("Bybit API response:", response.json())
    return response.json()

# === Ρίζα ===
@app.route("/")
def home():
    return "Bot is running!", 200

# === Webhook ===
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
    result = send_order(signal, symbol)

    return jsonify({"message": f"Trade executed: {signal} on {symbol}", "api_response": result}), 200

# === Εκκίνηση bot ===
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

