import requests
import time
import os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def get_data(symbol):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    return response.json()

def analyze(symbol):
    try:
        data = get_data(symbol)
        records = data["records"]["data"]
        pcr = data["records"]["pcr"]

        for item in records:
            if "CE" in item and "PE" in item:

                call_oi_change = item["CE"].get("changeinOpenInterest", 0)
                put_oi_change = item["PE"].get("changeinOpenInterest", 0)
                strike = item["strikePrice"]

                # ==============================
                # 🚫 NO TRADE ZONE (SIDEWAYS)
                # ==============================
                if (call_oi_change > 0 and put_oi_change > 0) or \
                   (call_oi_change < 0 and put_oi_change < 0) or \
                   (0.9 < pcr < 1.1):
                    return None

                # ==============================
                # 🟢 STRONG CALL BUY
                # ==============================
                if put_oi_change > 0 and call_oi_change < 0 and pcr > 1.2:
                    return f"🟢 {symbol} CALL BUY near {strike}"

                # ==============================
                # 🔴 STRONG PUT BUY
                # ==============================
                if call_oi_change > 0 and put_oi_change < 0 and pcr < 0.8:
                    return f"🔴 {symbol} PUT BUY near {strike}"

        return None

    except Exception as e:
        return None

# 🔥 Stocks (keep focused for quality)
stocks = [
    "NIFTY", "BANKNIFTY", "RELIANCE", "HDFCBANK",
    "ICICIBANK", "INFY", "TCS", "SBIN", "LT"
]

def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    return 9 <= now.hour <= 15

# ============================
# 🔄 MAIN LOOP
# ============================
while True:

    if not is_market_open():
        time.sleep(60)
        continue

    signals = []

    for stock in stocks:
        result = analyze(stock)
        if result:
            signals.append(result)

    if signals:
        message = "🚀 HIGH PROBABILITY TRADES\n\n" + "\n".join(signals[:3])
        send_message(message)
    else:
        send_message("📊 MARKET UPDATE\nNo A-grade setup. Stay patient.")

    time.sleep(300)  # 5 minutes
