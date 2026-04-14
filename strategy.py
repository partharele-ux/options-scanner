def generate_signal(data):

    # CALL BUY
    if data["price"] > data["resistance"]:
        if data["call_oi_change"] < 0:
            if data["gex"] < 0 and data["dex"] < 0:
                return "BUY CALL"

    # PUT BUY
    if data["price"] < data["support"]:
        if data["put_oi_change"] < 0:
            if data["gex"] < 0:
                return "BUY PUT"

    return None
