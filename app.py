‎from flask import Flask, request
‎import sqlite3
‎from telegram import Bot, Update
‎from telegram.ext import Dispatcher, CommandHandler, CallbackContext
‎from config import TOKEN
‎
‎app = Flask(Crypto_facuet_HUB_bot)
‎bot = Bot(8529856161:AAFg3N3R1uwNcuaHds-rUJeZFFgA7kVTECM)
‎
‎# Database setup
‎conn = sqlite3.connect("database.db", check_same_thread=False)
‎cursor = conn.cursor()
‎cursor.execute("""
‎CREATE TABLE IF NOT EXISTS users (
‎    user_id INTEGER PRIMARY KEY,
‎    referrer INTEGER,
‎    referrals INTEGER DEFAULT 0
‎)
‎""")
‎conn.commit()
‎
‎# Command: /start
‎def start(update: Update, context: CallbackContext):
‎    user = update.effective_user
‎    user_id = user.id
‎    referrer = int(context.args[0]) if context.args else None
‎
‎    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
‎    if not cursor.fetchone():
‎        cursor.execute("INSERT INTO users (user_id, referrer, referrals) VALUES (?, ?, 0)", (user_id, referrer))
‎        conn.commit()
‎        if referrer and referrer != user_id:
‎            cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id=?", (referrer,))
‎            conn.commit()
‎
‎    me = bot.get_me()
‎    link = f"https://t.me/{me.username}?start={user_id}"
‎    cursor.execute("SELECT referrals FROM users WHERE user_id=?", (user_id,))
‎    count = cursor.fetchone()[0]
‎    update.message.reply_text(f"Hello {user.first_name}\nInvite: {link}\nReferrals: {count}")
‎
‎# Command: /refs
‎def refs(update: Update, context: CallbackContext):
‎    user_id = update.effective_user.id
‎    cursor.execute("SELECT referrals FROM users WHERE user_id=?", (user_id,))
‎    data = cursor.fetchone()
‎    update.message.reply_text(f"Your referrals: {data[0]}" if data else "No data found.")
‎
‎# Dispatcher
‎dispatcher = Dispatcher(bot, None, workers=0)
‎dispatcher.add_handler(CommandHandler("start", start))
‎dispatcher.add_handler(CommandHandler("refs", refs))
‎
‎# Webhook route
‎@app.route('/webhook', methods=['POST'])
‎def webhook():
‎    update = Update.de_json(request.get_json(force=True), bot)
‎    dispatcher.process_update(update)
‎    return "ok"
‎
‎# Run server
‎if __name__ == "__main__":
‎    app.run(port=5000)
