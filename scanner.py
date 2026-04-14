import requests
import time
from datetime import datetime

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

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
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    return response.json()

def analyze(symbol):
    try:
        data = get_option_chain(symbol)
        records = data["records"]["data"]

        best_signal = None

        for item in records:
            if "CE" in item and "PE" in item:
                ce = item["CE"]
                pe = item["PE"]

                strike = item["strikePrice"]

                call_oi = ce.get("openInterest", 0)
                put_oi = pe.get("openInterest", 0)

                call_oi_change = ce.get("changeinOpenInterest", 0)
                put_oi_change = pe.get("changeinOpenInterest", 0)

                call_vol = ce.get("totalTradedVolume", 0)
                put_vol = pe.get("totalTradedVolume", 0)

                # 🎯 STRONG CALL SIGNAL
                if call_oi_change < -50000 and call_vol > 50000:
                    best_signal = f"""
{symbol} BUY CALL 📈
Strike: {strike}
Reason: Call OI unwinding + volume spike
Confidence: HIGH
"""
                    break

                # 🎯 STRONG PUT SIGNAL
                if put_oi_change < -50000 and put_vol > 50000:
                    best_signal = f"""
{symbol} BUY PUT 📉
Strike: {strike}
Reason: Put OI unwinding + volume spike
Confidence: HIGH
"""
                    break

        return best_signal

    except Exception as e:
        return None

# 🔥 F&O STOCK LIST (EXPANDABLE)
stocks = [
    "RELIANCE","SBIN","TATAMOTORS","INFY","HDFCBANK",
    "ICICIBANK","AXISBANK","LT","ITC","KOTAKBANK",
    "NIFTY","BANKNIFTY"
]

def run():
    if not is_market_open():
        print("Market closed")
        return

    send_message("Scanner running... 🚀")

    for stock in stocks:
        signal = analyze(stock)
        if signal:
            send_message(signal)
        time.sleep(1)

if __name__ == "__main__":
    run()
