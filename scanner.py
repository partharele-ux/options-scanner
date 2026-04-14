import requests
import time
from datetime import datetime

# ⚠️ REPLACE THIS WITH NEW TOKEN AFTER REVOKE
BOT_TOKEN = "8681437580:AAEdZ_aclCZzGE1C04olNCnehdPrIPU6zhQ"

# ✅ YOUR CHAT ID
CHAT_ID = "678428512"

def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    if now.hour < 9 or now.hour > 15:
        return False
    if now.hour == 9 and now.minute < 15:
        return False
    if now.hour == 15 and now.minute > 30:
        return False
    return True

def get_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}" \
        if symbol in ["NIFTY", "BANKNIFTY"] \
        else f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    return response.json()

def get_market_trend():
    try:
        data = get_option_chain("NIFTY")
        records = data["records"]["data"]

        total_call_oi = 0
        total_put_oi = 0

        for item in records:
            if "CE" in item:
                total_call_oi += item["CE"].get("openInterest", 0)
            if "PE" in item:
                total_put_oi += item["PE"].get("openInterest", 0)

        return "BULLISH" if total_put_oi > total_call_oi else "BEARISH"

    except:
        return "NEUTRAL"

def analyze(symbol, trend):
    try:
        data = get_option_chain(symbol)
        records = data["records"]["data"]
        spot = data["records"]["underlyingValue"]

        for item in records:
            if "CE" in item and "PE" in item:
                strike = item["strikePrice"]

                if abs(strike - spot) > 200:
                    continue

                ce = item["CE"]
                pe = item["PE"]

                call_oi_change = ce.get("changeinOpenInterest", 0)
                put_oi_change = pe.get("changeinOpenInterest", 0)

                call_vol = ce.get("totalTradedVolume", 0)
                put_vol = pe.get("totalTradedVolume", 0)

                ltp_call = ce.get("lastPrice", 0)
                ltp_put = pe.get("lastPrice", 0)

                if trend == "BULLISH":
                    if call_oi_change < -50000 and call_vol > 50000:
                        entry = round(ltp_call, 1)
                        return f"""
{symbol} BUY CALL 📈
Strike: {strike}
Entry: {entry}
SL: {round(entry * 0.75, 1)}
Target: {round(entry * 1.5, 1)}
Trend: {trend}
Confidence: HIGH
"""

                if trend == "BEARISH":
                    if put_oi_change < -50000 and put_vol > 50000:
                        entry = round(ltp_put, 1)
                        return f"""
{symbol} BUY PUT 📉
Strike: {strike}
Entry: {entry}
SL: {round(entry * 0.75, 1)}
Target: {round(entry * 1.5, 1)}
Trend: {trend}
Confidence: HIGH
"""

        return None

    except:
        return None

stocks = [
    "RELIANCE","SBIN","TATAMOTORS","INFY","HDFCBANK",
    "ICICIBANK","AXISBANK","LT","ITC","KOTAKBANK",
    "NIFTY","BANKNIFTY"
]

def run():
    if not is_market_open():
        print("Market closed")
        return

    trend = get_market_trend()
    send_message(f"📊 Market Trend: {trend}")

    for stock in stocks:
        signal = analyze(stock, trend)
        if signal:
            send_message(signal)
        time.sleep(1)

if __name__ == "__main__":
    run()
