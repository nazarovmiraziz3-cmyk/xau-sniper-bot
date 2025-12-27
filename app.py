from flask import Flask, request
import requests
from datetime import datetime, timedelta

TOKEN = "8474563790:AAHrDxceBdskOzVsPgxkwX23O9ipCAJhwas"
CHAT_ID = "2627850088"

app = Flask(__name__)

signals = {}
win = 0
loss = 0

def now_uz():
    return datetime.utcnow() + timedelta(hours=5)

current_day = now_uz().date()

def send(text, reply=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    if reply:
        data["reply_to_message_id"] = reply
    r = requests.post(url, json=data)
    if r.ok:
        return r.json()["result"]["message_id"]
    return None

def daily_stats():
    total = win + loss
    wr = round((win / total) * 100, 2) if total else 0
    send(
        "📊 DAILY STATS (XAUUSD M1)\n\n"
        "🕔 UTC+5\n"
        f"✅ TP: {win}\n"
        f"❌ SL: {loss}\n"
        f"📈 Winrate: {wr}%"
    )

@app.route("/webhook", methods=["POST"])
def webhook():
    global win, loss, current_day

    if now_uz().date() != current_day:
        daily_stats()
        win = loss = 0
        signals.clear()
        current_day = now_uz().date()

    text = request.json.get("message", "")

    if "🆔 ID:" in text and ("BUY SNIPER" in text or "SELL SNIPER" in text):
        sid = text.split("ID:")[1].split("\n")[0].strip()
        msg_id = send(text)
        signals[sid] = msg_id

    elif text.startswith("TP✅") and "ID:" in text:
        sid = text.split("ID:")[1].strip()
        if sid in signals:
            win += 1
            send("TP✅", signals[sid])
            signals.pop(sid)

    elif text.startswith("SL❌") and "ID:" in text:
        sid = text.split("ID:")[1].strip()
        if sid in signals:
            loss += 1
            send("SL❌", signals[sid])
            signals.pop(sid)

    return "ok"

@app.route("/")
def home():
    return "XAU SNIPER BOT RUNNING"

app.run(host="0.0.0.0", port=10000)
