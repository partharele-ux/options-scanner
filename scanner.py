import requests
import time
import os
from datetime import datetime
import pytz

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# F&O + Indices
SYMBOLS = [
    "NIFTY", "BANKNIFTY", "RELIANCE", "SBIN", "TATAMOTORS",
    "INFY", "HDFCBANK", "ICICIBANK", "AXISBANK",
    "LT", "ITC", "KOTAKBANK"
]

# =========================
# TELEGRAM
# =========================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


# =========================
# MARKET HOURS
# =========================
def is_market_open():
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)

    if now.weekday() >= 5:
        return False

    start = now.replace(hour=9, minute=15, second=0)
    end = now.replace(hour=15, minute=30, second=0)

    return start <= now <= end


# =========================
# DATA FETCH
# =========================
def get_option_chain(symbol):
    try:
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

        if symbol in ["NIFTY", "BANKNIFTY"]:
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
        }

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)

        response = session.get(url, headers=headers)
        return response.json()

    except:
        return None


# =========================
# ANALYSIS ENGINE
# =========================
def analyze(symbol):
    data = get_option_chain(symbol)

    if not data:
        return None

    try:
        records = data["records"]["data"]
        underlying = data["records"]["underlyingValue"]

        best_signal = None

        for item in records:
            if "CE" in item and "PE" in item:

                strike = item["strikePrice"]

                # Focus near ATM (important)
                if abs(strike - underlying) > 200:
                    continue

                call_oi = item["CE"].get("changeinOpenInterest", 0)
                put_oi = item["PE"].get("changeinOpenInterest", 0)

                # Strong directional signals
                if call_oi < -50000 and put_oi > 50000:
                    return f"🔥 {symbol}: BUY CALL near {strike}"

                if put_oi < -50000 and call_oi > 50000:
                    return f"🔥 {symbol}: BUY PUT near {strike}"

        return None

    except:
        return None


# =========================
# MAIN SCANNER
# =========================
def run():
    signals = []

    for symbol in SYMBOLS:
        signal = analyze(symbol)

        if signal:
            signals.append(signal)

        time.sleep(1)  # avoid blocking

    if signals:
        final_msg = "🚀 TOP TRADES:\n\n" + "\n".join(signals[:5])
        send_message(final_msg)
    else:
        print("No strong signals")


# =========================
# EXECUTION
# =========================
if __name__ == "__main__":
    if is_market_open():
        run()
    else:
        print("Market closed")
