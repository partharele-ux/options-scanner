import requests
import time
from telegram_bot import send_message

# -------------------------------
# FETCH NSE OPTION CHAIN
# -------------------------------
def get_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

    session = requests.Session()

    try:
        # Get cookies
        session.get("https://www.nseindia.com", headers=headers)
        time.sleep(1)

        # Fetch data
        response = session.get(url, headers=headers)

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


# -------------------------------
# ANALYSIS LOGIC (ATM BASED)
# -------------------------------
def analyze(symbol):
    try:
        data = get_option_chain(symbol)

        if not data:
            return f"{symbol} - Data fetch failed"

        records = data["records"]["data"]
        spot = data["records"].get("underlyingValue", 0)

        closest = None
        min_diff = float("inf")

        # Find ATM strike
        for item in records:
            strike = item.get("strikePrice", 0)
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

        strike = closest.get("strikePrice", 0)

        # -------------------------------
        # STRATEGY LOGIC
        # -------------------------------
        if call_oi_change < 0 and put_oi_change > 0:
            return f"{symbol}: BUY CALL near {strike}"

        if put_oi_change < 0 and call_oi_change > 0:
            return f"{symbol}: BUY PUT near {strike}"

        return f"{symbol}: No clear signal"

    except Exception as e:
        return f"{symbol} ERROR: {str(e)}"


# -------------------------------
# STOCK LIST (SAFE LIMIT)
# -------------------------------
stocks = [
    "RELIANCE","SBIN","TATAMOTORS","INFY","HDFCBANK",
    "ICICIBANK","AXISBANK","LT","ITC","KOTAKBANK"
]


# -------------------------------
# MAIN EXECUTION
# -------------------------------
for stock in stocks:
    signal = analyze(stock)

    # Send only actionable signals
    if "BUY" in signal:
        send_message(signal)

    print(signal)  # for logs

    time.sleep(2)  # avoid NSE blocking
