import requests
import time
import os
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ======================
# FULL F&O STOCK LIST
# ======================
ALL_SYMBOLS = [
    "NIFTY","BANKNIFTY",
    "HDFCBANK","ICICIBANK","AXISBANK","SBIN","KOTAKBANK","INDUSINDBK","PNB","BANKBARODA",
    "INFY","TCS","WIPRO","HCLTECH","TECHM",
    "RELIANCE","LT","ITC","ASIANPAINT","ULTRACEMCO",
    "TATAMOTORS","MARUTI","M&M","HEROMOTOCO","EICHERMOT",
    "BAJFINANCE","BAJAJFINSV","HDFCLIFE","SBILIFE","ICICIPRULI",
    "ADANIPORTS","ADANIENT","JSWSTEEL","TATASTEEL","COALINDIA","POWERGRID"
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
# ROTATION SYSTEM
# ======================
def get_batch():
    now = get_time()
    batch_size = 8

    index = (now.minute // 5 * batch_size) % len(ALL_SYMBOLS)
    return ALL_SYMBOLS[index:index + batch_size]

# ======================
# FETCH DATA
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
# ANALYSIS (BALANCED)
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

        for r in records:
            if "CE" in r and "PE" in r:
                call_total += r["CE"].get("changeinOpenInterest", 0)
                put_total += r["PE"].get("changeinOpenInterest", 0)

        # ======================
        # BIAS
        # ======================
        if put_total > call_total:
            direction = "CALL 🟢"
            entry = round(price + 10, 2)
            sl = round(price - 70, 2)
            target = round(price + 120, 2)

        else:
            direction = "PUT 🔴"
            entry = round(price - 10, 2)
            sl = round(price + 70, 2)
            target = round(price - 120, 2)

        return f"""{symbol} {direction}
Entry: {entry}
SL: {sl}
Target: {target}"""

    except:
        return None

# ======================
# MAIN ENGINE
# ======================
def run():
    symbols = get_batch()

    trades = []

    for sym in symbols:
        t = analyze(sym)

        if t:
            trades.append(t)

        time.sleep(1)

    msg = "📊 LIVE TRADING ENGINE\n\n"

    if trades:
        msg += "\n\n".join(trades[:4])  # max 4 trades
    else:
        msg += "⚠️ No setups in this batch"

    send_message(msg)

# ======================
# EXECUTE
# ======================
if __name__ == "__main__":
    run()
