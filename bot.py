import os, asyncio, time
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- 1. RENDER HEARTBEAT (Keep Alive) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIG ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- 3. PROGRESS LOGIC ---
async def fast_progress(current, total, status, action):
    # በየ 10% ልዩነት ብቻ ሜሴጅ እንዲያድስ (ለፍጥነት)
    percent = (current / total) * 100
    if int(percent) % 10 == 0:
        try:
            await status.edit(f"🚀 **{action}**: {percent:.1f}%")
        except: pass

# --- 4. THE HANDLER (ሁሉንም ሊንክ እንዲቀበል) ---
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # ማንኛውንም የቴሌግራም ሊንክ ካገኘ ስራ ይጀምራል
    if "t.me/" in event.text:
        status = await event.reply("📂 **ሊንኩን በማረጋገጥ ላይ...**")
        try:
            # ሊንኩን መተንተን
            link = event.text.split('/')
            msg_id = int(link[-1])
            
            # ለ Private (t.me/c/...) እና ለ Public ቻናሎች
            if "t.me/c/" in event.text:
                chat = int("-100" + link[-2])
            else:
                chat = link[-2]

            msg = await client.get_messages(chat, ids=msg_id)
            
            if not msg or not msg.media:
                return await status.edit("❌ በዚህ ሊንክ ላይ ፋይል አልተገኘም!")

            name = msg.file.name or "file.mp4"
            await status.edit(f"📥 **በማውረድ ላይ:** `{name}`")

            # --- FAST DOWNLOAD ---
            path = await client.download_media(
                msg,
                progress_callback=lambda c, t: fast_progress(c, t, status, "Downloading")
            )

            await status.edit(f"📤 **በመላክ ላይ:** `{name}`")

            # --- FAST UPLOAD (ወደ Saved Messages) ---
            await client.send_file(
                'me', 
                path, 
                force_document=True,
                caption=f"✅ `{name}`",
                progress_callback=lambda c, t: fast_progress(c, t, status, "Uploading")
            )

            if os.path.exists(path): os.remove(path)
            await status.delete()

        except Exception as e:
            await status.edit(f"❌ ስህተት: {str(e)}")

# --- 5. START ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    client.start()
    print("Bot started! Send any telegram link to your saved messages.")
    client.run_until_disconnected()
