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

    spot = data["records"]["underlyingValue"]

closest = None
min_diff = float("inf")

# Find ATM strike
for item in records:
    strike = item["strikePrice"]
    diff = abs(strike - spot)

    if diff < min_diff:
        min_diff = diff
        closest = item

if not closest:
    return f"{symbol}: No data"

ce = closest.get("CE", {})
pe = closest.get("PE", {})

call_oi_change = ce.get("changeinOpenInterest", 0)
put_oi_change = pe.get("changeinOpenInterest", 0)

strike = closest["strikePrice"]

# STRONG LOGIC
if call_oi_change < 0 and put_oi_change > 0:
    return f"{symbol}: BUY CALL near {strike}"

if put_oi_change < 0 and call_oi_change > 0:
    return f"{symbol}: BUY PUT near {strike}"

return f"{symbol}: No clear signal"
    return f"{symbol}: No signal"

stocks = [
    "RELIANCE","SBIN","TATAMOTORS","INFY","HDFCBANK",
    "ICICIBANK","AXISBANK","LT","ITC","KOTAKBANK"
]

for stock in stocks:
    signal = analyze(stock)
    if "BUY" in signal:
    send_message(signal)
    time.sleep(2)  # avoid blocking

from datetime import datetime

def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:  # Sat/Sun
        return False
    if now.hour < 9 or now.hour > 15:
        return False
    return True

if not is_market_open():
    print("Market closed")
    exit()
