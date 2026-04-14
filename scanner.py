from telegram_bot import send_message

# TEMP TEST DATA
data = {
    "price": 1000,
    "resistance": 990,
    "support": 950,
    "call_oi_change": -100,
    "put_oi_change": 50,
    "gex": -5,
    "dex": -3
}

# SIMPLE LOGIC
if data["price"] > data["resistance"]:
    if data["call_oi_change"] < 0 and data["gex"] < 0:
        send_message("BUY CALL SIGNAL 🚀")
else:
    send_message("Scanner running - no signal")
