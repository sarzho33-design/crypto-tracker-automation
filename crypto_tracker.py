import os
import requests
from datetime import datetime, timezone

# ---- CONFIG ----
SHEETDB_URL = "https://sheetdb.io/api/v1/x01x3eh5igbxi"
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Alert threshold — % move (up or down) required to trigger a Telegram alert.
# Bump this up/down as you tune signal quality.
THRESHOLD_PERCENT = 2.0


# ---- FETCH CURRENT PRICES ----
def fetch_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    btc_price = data["bitcoin"]["usd"]
    eth_price = data["ethereum"]["usd"]
    return btc_price, eth_price


# ---- READ PREVIOUS PRICES FROM SHEET ----
def get_previous_prices():
    """
    Reads the last logged row from the sheet and parses the previous
    BTC/ETH prices out of the "Price (USD)" column (format: "65339 / 1895.3").
    Returns (None, None) if the sheet is empty or the row can't be parsed
    (e.g. this is the very first run).
    """
    response = requests.get(SHEETDB_URL, timeout=15)
    response.raise_for_status()
    rows = response.json()

    if not rows:
        return None, None

    last_row = rows[-1]
    price_str = last_row.get("Price (USD)", "")

    try:
        btc_str, eth_str = price_str.split("/")
        return float(btc_str.strip()), float(eth_str.strip())
    except (ValueError, AttributeError):
        return None, None


# ---- CALCULATE % CHANGE ----
def calculate_change(current_price, previous_price):
    if previous_price is None or previous_price == 0:
        return None
    return ((current_price - previous_price) / previous_price) * 100


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


# ---- SEND TELEGRAM MOVEMENT ALERT ----
def send_movement_alert(symbol, current_price, previous_price, change_pct):
    sign = "+" if change_pct >= 0 else ""
    message = (
        f"🚨 {symbol} MOVE\n"
        f"{symbol}: ${current_price:,.2f}\n"
        f"{sign}{change_pct:.2f}% in ~1h\n"
        f"Previous: ${previous_price:,.2f}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, data=payload, timeout=15)
    response.raise_for_status()


# ---- MAIN ----
def main():
    btc_price, eth_price = fetch_prices()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Read the previous observation BEFORE writing the new one.
    prev_btc, prev_eth = get_previous_prices()

    write_to_sheet(btc_price, eth_price, timestamp)

    btc_change = calculate_change(btc_price, prev_btc)
    eth_change = calculate_change(eth_price, prev_eth)

    alerts_sent = []

    if btc_change is not None and abs(btc_change) >= THRESHOLD_PERCENT:
        send_movement_alert("BTC", btc_price, prev_btc, btc_change)
        alerts_sent.append(f"BTC ({btc_change:+.2f}%)")

    if eth_change is not None and abs(eth_change) >= THRESHOLD_PERCENT:
        send_movement_alert("ETH", eth_price, prev_eth, eth_change)
        alerts_sent.append(f"ETH ({eth_change:+.2f}%)")

    print(
        f"Logged BTC ${btc_price} / ETH ${eth_price} at {timestamp}. "
        f"Alerts sent: {', '.join(alerts_sent) if alerts_sent else 'none'}"
    )


if __name__ == "__main__":
    main()
