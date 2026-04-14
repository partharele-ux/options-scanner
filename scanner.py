import requests
import time
import os
from datetime import datetime

# 🔐 FROM GITHUB SECRETS
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

stocks = [
    "NIFTY","BANKNIFTY","SENSEX",
    "RELIANCE","HDFCBANK","ICICIBANK","SBIN","AXISBANK",
    "INFY","TCS","LT","KOTAKBANK","ITC",
    "TATAMOTORS","MARUTI","BAJFINANCE","BAJAJFINSV",
    "ADANIPORTS","ASIANPAINT","SUNPHARMA","HINDUNILVR"
]

MAX_TRADES = 5


# ==============================
# TELEGRAM
# ==============================
def send_message(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram error:", e)


# ==============================
# NSE DATA
# ==============================
def get_data(symbol):
    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        headers = {"User-Agent": "Mozilla/5.0"}

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        res = session.get(url, headers=headers)

        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("Data error:", e)

    return None


# ==============================
# ANALYSIS
# ==============================
def analyze(symbol):
    data = get_data(symbol)
    if not data:
        return None

    underlying = data["records"]["underlyingValue"]
    records = data["records"]["data"]

    total_call = 0
    total_put = 0

    atm = None
    min_diff = float("inf")

    for item in records:
        if "CE" in item and "PE" in item:
            strike = item["strikePrice"]

            call_oi = item["CE"].get("changeinOpenInterest", 0)
            put_oi = item["PE"].get("changeinOpenInterest", 0)

            total_call += call_oi
            total_put += put_oi

            if abs(strike - underlying) < min_diff:
                min_diff = abs(strike - underlying)
                atm = strike

    if atm is None:
        return None

    strength = abs(total_call - total_put)

    # 🔥 FILTER WEAK SIGNALS
    if strength < 50000:
        return None

    if total_call > total_put * 1.3:
        return {
            "symbol": symbol,
            "direction": "BEARISH",
            "trade": f"BUY {atm} PE",
            "strength": strength
        }

    elif total_put > total_call * 1.3:
        return {
            "symbol": symbol,
            "direction": "BULLISH",
            "trade": f"BUY {atm} CE",
            "strength": strength
        }

    return None


# ==============================
# TIME FILTERS
# ==============================
def is_market_open():
    now = datetime.now()

    if now.weekday() >= 5:
        return False

    start = now.replace(hour=9, minute=20)
    end = now.replace(hour=15, minute=20)

    return start <= now <= end


def is_good_time():
    now = datetime.now()

    hour = now.hour
    minute = now.minute

    # Avoid early noise
    if hour == 9 and minute < 25:
        return False

    # Avoid midday chop
    if (hour == 11 and minute > 30) or (hour == 12) or (hour == 13 and minute < 15):
        return False

    return True


# ==============================
# ENGINE
# ==============================
def run():
    send_message("🚀 Trading Engine Live")

    while True:
        if is_market_open() and is_good_time():

            results = []

            for stock in stocks:
                res = analyze(stock)
                if res:
                    results.append(res)
                time.sleep(1)

            # 🔥 SORT BEST TRADES
            results = sorted(results, key=lambda x: x["strength"], reverse=True)
            top_trades = results[:MAX_TRADES]

            if top_trades:
                message = "📊 TOP 5 TRADES:\n\n"

                for trade in top_trades:
                    message += f"{trade['symbol']} | {trade['direction']}\n"
                    message += f"{trade['trade']}\n\n"

                send_message(message)

            time.sleep(180)

        else:
            time.sleep(300)


if __name__ == "__main__":
    run()
