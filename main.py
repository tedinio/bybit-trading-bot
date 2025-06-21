from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
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

    # Εδώ στο μέλλον θα μπει η σύνδεση με Bybit API

    return jsonify({"message": f"Trade executed: {signal} on {symbol}"}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
