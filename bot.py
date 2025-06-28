import telebot
import os
from flask import Flask, request
import json
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Ayan123")
TON_ADDRESS = os.environ.get("TON_ADDRESS", "UQAMACDUf3...")  # Your wallet

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

users = load_data()

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {
            "vip": False,
            "joined": datetime.now().isoformat(),
            "ref": message.text.split()[1] if len(message.text.split()) > 1 else None
        }
        save_data(users)
    bot.send_message(message.chat.id, f"Welcome to TON Mining Bot!\nWallet: {TON_ADDRESS}")

@bot.message_handler(commands=["vip"])
def vip_status(message):
    user_id = str(message.chat.id)
    status = "✅ Active" if users.get(user_id, {}).get("vip") else "❌ Not Active"
    bot.send_message(message.chat.id, f"Your VIP status: {status}")

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.text.split(" ")[-1] == ADMIN_PASSWORD:
        total_users = len(users)
        vip_users = sum(1 for u in users.values() if u.get("vip"))
        bot.send_message(message.chat.id, f"👥 Total Users: {total_users}\n⭐ VIP Users: {vip_users}")
    else:
        bot.send_message(message.chat.id, "❌ Invalid admin password.")

# Flask webhook setup (optional for render with polling)
@app.route("/")
def home():
    return "Bot is running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Polling fallback
if __name__ == "__main__":
    bot.infinity_polling()