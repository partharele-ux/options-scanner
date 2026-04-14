from strategy import generate_signal
from telegram_bot import send_message
import random

stocks = ["RELIANCE", "SBIN", "TATAMOTORS", "ICICIBANK"]

def fake_data():
    return {
        "price": random.randint(900,1100),
        "resistance": 1000,
        "support": 950,
        "call_oi_change": random.randint(-1000,1000),
        "put_oi_change": random.randint(-1000,1000),
        "gex": random.randint(-10,10),
        "dex": random.randint(-10,10)
    }

for stock in stocks:

    data = fake_data()

    signal = generate_signal(data)

    if signal:
        msg = f"{stock}\n{signal}\nGEX: {data['gex']} DEX: {data['dex']}"
        send_message(msg)
