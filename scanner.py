import requests
import time
import os
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = [
    "NIFTY","BANKNIFTY",
    "RELIANCE","SBIN","INFY",
    "HDFCBANK","ICICIBANK","AXISBANK"
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
# TIME
# ======================
def get_time():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz)

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
# ANALYSIS (SMART FILTER)
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

        best_trade = None

        for r in records:
            if "CE" in r and "PE" in r:

                strike = r["strikePrice"]

                # Focus ATM ±150
                if abs(strike - price) > 150:
                    continue

                call_oi = r["CE"].get("changeinOpenInterest", 0)
                put_oi = r["PE"].get("changeinOpenInterest", 0)

                call_total += call_oi
                put_total += put_oi

                # 🔥 STRONG CONDITION ONLY
                if call_oi < -20000 and put_oi > 20000:
                    entry = round(price + 10, 2)
                    sl = round(price - 80, 2)
                    target = round(price + 150, 2)

                    best_trade = f"""
{symbol} 🟢 CALL

Entry: {entry}
SL: {sl}
Target: {target}
"""

                elif put_oi < -20000 and call_oi > 20000:
                    entry = round(price - 10, 2)
                    sl = round(price + 80, 2)
                    target = round(price - 150, 2)

                    best_trade = f"""
{symbol} 🔴 PUT

Entry: {entry}
SL: {sl}
Target: {target}
"""

        return best_trade

    except:
        return None

# ======================
# MAIN ENGINE
# ======================
def run():
    trades = []

    for sym in SYMBOLS:
        trade = analyze(sym)

        if trade:
            trades.append(trade)

        time.sleep(1)

    msg = "📊 TRADING SETUPS\n\n"

    if trades:
        # Limit best 3
        msg += "\n".join(trades[:3])
    else:
        msg += "⚠️ No high-probability trades right now"

    send_message(msg)

# ======================
# EXECUTE
# ======================
if __name__ == "__main__":
    run()
