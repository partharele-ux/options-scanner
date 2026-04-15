import requests
import time
import os
from datetime import datetime
import pytz

# =========================
# CONFIG (ADD YOUR VALUES)
# =========================
BOT_TOKEN = "8681437580:AAEdZ_aclCZzGE1C04olNCnehdPrIPU6zhQ"
CHAT_ID = "678428512"

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
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass


# =========================
# MARKET HOURS
# =========================
def is_market_open():
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)

    if now.weekday() >= 5:
        return False

    start = now.replace(hour=9, minute=15)
    end = now.replace(hour=15, minute=30)

    return start <= now <= end


# =========================
# FETCH DATA
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
# ANALYSIS (CONSISTENT LOGIC)
# =========================
def analyze(symbol):
    data = get_option_chain(symbol)

    if not data:
        return None, None

    try:
        records = data["records"]["data"]
        underlying = data["records"]["underlyingValue"]

        call_strength = 0
        put_strength = 0
        best_trade = None

        for item in records:
            if "CE" in item and "PE" in item:

                strike = item["strikePrice"]

                # Focus ATM ±300
                if abs(strike - underlying) > 300:
                    continue

                call_oi = item["CE"].get("changeinOpenInterest", 0)
                put_oi = item["PE"].get("changeinOpenInterest", 0)

                call_strength += call_oi
                put_strength += put_oi

                # Trade logic (relaxed → more signals)
                if call_oi < -20000 and put_oi > 20000:
                    best_trade = f"BUY CALL near {strike}"

                if put_oi < -20000 and call_oi > 20000:
                    best_trade = f"BUY PUT near {strike}"

        # Market bias
        bias = "SIDEWAYS"
        if put_strength > call_strength:
            bias = "BULLISH"
        elif call_strength > put_strength:
            bias = "BEARISH"

        return best_trade, bias

    except:
        return None, None


# =========================
# MAIN ENGINE
# =========================
def run():
    trades = []
    biases = []

    for symbol in SYMBOLS:
        trade, bias = analyze(symbol)

        if bias:
            biases.append(f"{symbol}: {bias}")

        if trade:
            trades.append(f"{symbol}: {trade}")

        time.sleep(1)

    # Always send update (NO SILENCE)
    message = "📊 MARKET UPDATE\n\n"

    if biases:
        message += "Bias:\n" + "\n".join(biases[:5]) + "\n\n"

    if trades:
        message += "🚀 Trades:\n" + "\n".join(trades[:5])
    else:
        message += "⚠️ No strong trades, wait"

    send_message(message)


# =========================
# EXECUTION
# =========================
if __name__ == "__main__":
    if is_market_open():
        run()
    else:
        print("Market closed")
