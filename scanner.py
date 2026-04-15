import requests
import time
import os
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = [
    "NIFTY","BANKNIFTY",
    "RELIANCE","HDFCBANK","ICICIBANK",
    "SBIN","INFY","AXISBANK"
]

# ======================
# TELEGRAM
# ======================
def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ======================
# TIME FILTER (LOOSENED)
# ======================
def valid_time():
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)

    if now.hour < 9 or now.hour > 15:
        return False

    return True

# ======================
# DATA FETCH
# ======================
def get_data(symbol):
    try:
        if symbol in ["NIFTY","BANKNIFTY"]:
            url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        else:
            url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

        headers = {"User-Agent": "Mozilla/5.0"}

        s = requests.Session()
        s.get("https://www.nseindia.com", headers=headers)
        res = s.get(url, headers=headers)

        return res.json()
    except:
        return None

# ======================
# ANALYSIS (HYBRID)
# ======================
def analyze(symbol):
    data = get_data(symbol)
    if not data:
        return None

    try:
        records = data["records"]["data"]
        price = data["records"]["underlyingValue"]

        call_total = 0
        put_total = 0

        strong_signal = None
        medium_signal = None

        for r in records:
            if "CE" in r and "PE" in r:

                strike = r["strikePrice"]

                if abs(strike - price) > 200:
                    continue

                call_oi = r["CE"].get("changeinOpenInterest", 0)
                put_oi = r["PE"].get("changeinOpenInterest", 0)

                call_total += call_oi
                put_total += put_oi

                # 🟢 HIGH CONFIDENCE
                if call_oi < -20000 and put_oi > 20000:
                    strong_signal = f"""
{symbol} 🟢 STRONG CALL

Entry: {round(price+10,2)}
SL: {round(price-80,2)}
Target: {round(price+150,2)}
"""

                elif put_oi < -20000 and call_oi > 20000:
                    strong_signal = f"""
{symbol} 🔴 STRONG PUT

Entry: {round(price-10,2)}
SL: {round(price+80,2)}
Target: {round(price-150,2)}
"""

                # ⚡ MEDIUM CONFIDENCE
                elif call_oi < -10000 and put_oi > 10000:
                    medium_signal = f"{symbol} ⚡ CALL near {strike}"

                elif put_oi < -10000 and call_oi > 10000:
                    medium_signal = f"{symbol} ⚡ PUT near {strike}"

        # Priority: strong > medium
        return strong_signal if strong_signal else medium_signal

    except:
        return None

# ======================
# MAIN
# ======================
def run():
    if not valid_time():
        print("Outside hours")
        return

    trades = []

    for sym in SYMBOLS:
        t = analyze(sym)

        if t:
            trades.append(t)

        time.sleep(1)

    msg = "📊 TRADING ENGINE\n\n"

    if trades:
        msg += "\n".join(trades[:4])  # max 4 trades
    else:
        msg += "⚠️ No setups currently"

    send_message(msg)

# ======================
# EXECUTE
# ======================
if __name__ == "__main__":
    run()
