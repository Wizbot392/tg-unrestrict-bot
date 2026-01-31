import os
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- FAKE WEB SERVER TO TRICK RENDER ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    if event.text and "t.me/" in event.text:
        # ... (Keep the rest of your download/upload logic here)
        pass

if __name__ == "__main__":
    keep_alive() # Starts the fake website
    print("Bot is starting...")
    client.start()
    client.run_until_disconnected()
