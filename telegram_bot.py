import requests

TOKEN = "8681437580:AAEeXNwvMFjPM2ITmC_M6wFYB65HP-cdYVw"
CHAT_ID = "678428512"

def send_message(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
