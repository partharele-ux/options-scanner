import requests
from telegram_bot import send_message

def get_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)

    response = session.get(url, headers=headers)
    data = response.json()

    return data

def analyze(symbol):
    data = get_option_chain(symbol)

    records = data["records"]["data"]

    for item in records:
        if item.get("CE") and item.get("PE"):

            call_oi_change = item["CE"].get("changeinOpenInterest", 0)
            put_oi_change = item["PE"].get("changeinOpenInterest", 0)

            strike = item["strikePrice"]

            # SIMPLE LOGIC
            if call_oi_change < 0:
                return f"{symbol} BUY CALL near {strike}"

            if put_oi_change < 0:
                return f"{symbol} BUY PUT near {strike}"

    return None

stocks = ["RELIANCE", "SBIN", "TATAMOTORS"]

for stock in stocks:
    signal = analyze(stock)

    if signal:
        send_message(signal)
