import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

# Render-এর Environment Variables থেকে এগুলো নেবে
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")

COINS = {
    "BTC/USDT": "bitcoin",
    "BNB/USDT": "binancecoin",
    "ETH/USDT": "ethereum",
    "SOL/USDT": "solana"
}


def get_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": ",".join(COINS.values()),
        "vs_currencies": "usd"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    return response.json()


def send_message(message):
    if not BOT_TOKEN or not CHANNEL:
        print("BOT_TOKEN or CHANNEL is missing")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHANNEL,
        "text": message
    }

    response = requests.post(url, data=data, timeout=20)

    print("Telegram:", response.text)


def update_prices():
    while True:
        try:
            prices = get_prices()

            message = "📊 CRYPTO PRICE UPDATE\n\n"

            for symbol, coin_id in COINS.items():
                price = prices.get(coin_id, {}).get("usd")

                if price is not None:
                    message += f"💰 {symbol}: ${price:,.2f}\n"
                else:
                    message += f"⚠️ {symbol}: Price unavailable\n"

            message += "\n⏱ Updated every 10 minutes"

            send_message(message)
            print(message)

        except Exception as error:
            print("ERROR:", error)

        time.sleep(600)


@app.route("/")
def home():
    return "Crypto Price Bot is running! ✅"


if __name__ == "__main__":
    thread = threading.Thread(target=update_prices, daemon=True)
    thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
