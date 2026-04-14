import requests
import time
from telegram_bot import send_message

def get_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

    session = requests.Session()

    # Step 1: Get cookies
    session.get("https://www.nseindia.com", headers=headers)
    time.sleep(1)

    # Step 2: Fetch data
    response = session.get(url, headers=headers)

    if response.status_code != 200:
        return None

    return response.json()

def analyze(symbol):
    data = get_option_chain(symbol)

    if not data:
        return f"{symbol} - Data fetch failed"

    records = data["records"]["data"]

    for item in records:
        if "CE" in item and "PE" in item:

            call_oi_change = item["CE"].get("changeinOpenInterest", 0)
            put_oi_change = item["PE"].get("changeinOpenInterest", 0)

            strike = item["strikePrice"]

            # SIMPLE LOGIC
            if call_oi_change < 0:
                return f"{symbol}: BUY CALL near {strike}"

            if put_oi_change < 0:
                return f"{symbol}: BUY PUT near {strike}"

    return f"{symbol}: No signal"

stocks = [
    "RELIANCE","SBIN","TATAMOTORS","INFY","HDFCBANK",
    "ICICIBANK","AXISBANK","LT","ITC","KOTAKBANK"
]

for stock in stocks:
    signal = analyze(stock)
    send_message(signal)
    time.sleep(2)  # avoid blocking
