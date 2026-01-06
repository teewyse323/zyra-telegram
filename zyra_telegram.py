import os
import requests
from flask import Flask, request

app = Flask(__name__)

def generate_message(name, occasion):
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        return f"Dear {name},\nHappy {occasion}! — Zyra"
    try:
        resp = requests.post(
            "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
            headers={"Authorization": f"Bearer {hf_token}"},
            json={"inputs": f"Write a warm {occasion} message for {name}.", "parameters": {"max_new_tokens": 100}},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"].split("\n")[0].strip()
    except:
        pass
    return f"Dear {name},\nHappy {occasion}! — Zyra"

def send_telegram_message(chat_id, text):
    bot_token = os.getenv("TELEGRAM_TOKEN")
    if not bot_token: return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route(f"/{os.getenv('TELEGRAM_TOKEN', 'webhook')}", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()
        if text.lower().startswith("zyra "):
            parts = text.split(maxsplit=2)
            if len(parts) >= 3:
                name, occasion = parts[1], parts[2]
                msg = generate_message(name, occasion)
                send_telegram_message(chat_id, msg)
            else:
                send_telegram_message(chat_id, "💡 Send: Zyra [Name] [Occasion]")
        else:
            send_telegram_message(chat_id, "✨ Try: Zyra Titi birthday")
    return "OK", 200

@app.route("/")
def home():
    return "Zyra is live 💬"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
