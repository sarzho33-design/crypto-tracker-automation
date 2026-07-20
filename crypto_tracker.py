import os
import requests
from datetime import datetime, timezone

# ---- CONFIG ----
SHEETDB_URL = "https://sheetdb.io/api/v1/x01x3eh5igbxi?sheet=Sheet2"
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# ---- FETCH PRICES ----
def fetch_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    btc_price = data["bitcoin"]["usd"]
    eth_price = data["ethereum"]["usd"]
    return btc_price, eth_price

# ---- WRITE TO GOOGLE SHEETS VIA SHEETDB ----
def write_to_sheet(btc_price, eth_price, timestamp):
    payload = {
        "data": [
            {
                "Coin": "bitcoin, ethereum",
                "Price (USD)": f"{btc_price} / {eth_price}",
                "Date": timestamp
            }
        ]
    }
    response = requests.post(SHEETDB_URL, json=payload, timeout=15)
    response.raise_for_status()

# ---- SEND TELEGRAM ALERT ----
def send_telegram_message(btc_price, eth_price, timestamp):
    message = (
        f"📊 Crypto Price Update\n"
        f"🕐 {timestamp}\n"
        f"₿ Bitcoin: ${btc_price:,.2f}\n"
        f"Ξ Ethereum: ${eth_price:,.2f}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, data=payload, timeout=15)
    response.raise_for_status()

# ---- MAIN ----
def main():
    btc_price, eth_price = fetch_prices()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    write_to_sheet(btc_price, eth_price, timestamp)
    send_telegram_message(btc_price, eth_price, timestamp)

    print(f"Success: BTC ${btc_price} / ETH ${eth_price} logged at {timestamp}")

if __name__ == "__main__":
    main()
