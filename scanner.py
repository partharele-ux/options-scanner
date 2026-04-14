import requests
import time
import os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

stocks = ["NIFTY","BANKNIFTY","RELIANCE","HDFCBANK","ICICIBANK","SBIN"]

MAX_TRADES = 5

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

trade_log = []
cache_data = {}
daily_sent = False


def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    session.post(url, data={"chat_id": CHAT_ID, "text": msg})


def get_data(symbol):
    try:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        session.get("https://www.nseindia.com")
        res = session.get(url, timeout=10)

        if res.status_code == 200:
            data = res.json()
            cache_data[symbol] = data
            return data
    except:
        return cache_data.get(symbol)

    return None


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

    if abs(total_call - total_put) < 50000:
        return None

    if total_call > total_put * 1.3:
        return {
            "symbol": symbol,
            "direction": "PUT",
            "entry_price": underlying,
            "strike": atm
        }

    elif total_put > total_call * 1.3:
        return {
            "symbol": symbol,
            "direction": "CALL",
            "entry_price": underlying,
            "strike": atm
        }

    return None


# 🔥 REAL P&L CALCULATION
def calculate_real_pnl():
    total_pnl = 0
    wins = 0
    losses = 0

    for trade in trade_log:
        data = get_data(trade["symbol"])
        if not data:
            continue

        current_price = data["records"]["underlyingValue"]
        entry = trade["entry_price"]

        if trade["direction"] == "CALL":
            pnl = current_price - entry
        else:
            pnl = entry - current_price

        total_pnl += pnl

        if pnl > 0:
            wins += 1
        else:
            losses += 1

    return wins, losses, total_pnl


def send_daily_report():
    global daily_sent

    if daily_sent:
        return

    wins, losses, pnl = calculate_real_pnl()
    total = wins + losses

    if total == 0:
        return

    winrate = round((wins / total) * 100, 2)

    msg = f"""
📊 LIVE P&L REPORT

Trades: {total}
Wins: {wins}
Losses: {losses}
Win Rate: {winrate}%
Net Points: {round(pnl,2)}
"""

    send_message(msg)
    daily_sent = True


def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    return now.replace(hour=9, minute=20) <= now <= now.replace(hour=15, minute=20)


def is_good_time():
    now = datetime.now()

    if now.hour == 9 and now.minute < 25:
        return False

    if (now.hour == 11 and now.minute > 30) or now.hour == 12 or (now.hour == 13 and now.minute < 15):
        return False

    return True


def run():
    send_message("🚀 Live P&L Engine Started")

    while True:
        now = datetime.now()

        if is_market_open() and is_good_time():

            results = []

            for stock in stocks:
                res = analyze(stock)
                if res:
                    results.append(res)
                time.sleep(2)

            results = results[:MAX_TRADES]

            if results:
                msg = "📊 TRADES:\n\n"

                for trade in results:
                    msg += f"{trade['symbol']} | {trade['direction']}\n"
                    msg += f"Entry: {round(trade['entry_price'],2)}\n\n"

                    trade_log.append(trade)

                send_message(msg)

            time.sleep(180)

        if now.hour >= 15 and now.minute >= 30:
            send_daily_report()

        time.sleep(60)


if __name__ == "__main__":
    run()
