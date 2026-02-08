import os, asyncio, time, random
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.network import ConnectionTcpFull

# --- 1. RENDER STAY-ALIVE ---
app = Flask(__name__)
@app.route('/')
def home(): return "Speed: Ultra | Status: Active"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIG ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

# Parallel ግንኙነት እንዲኖረው sequential_updates=False እናደርጋለን
client = TelegramClient(
    StringSession(STRING_SESSION), 
    API_ID, API_HASH,
    connection=ConnectionTcpFull,
    sequential_updates=False
)

# --- 3. FAST PROGRESS & ANTI-KILL ---
last_edit = 0

async def fast_progress(current, total, status, action):
    global last_edit
    now = time.time()
    # በየ 8 ሴኮንዱ ብቻ ሜሴጁን አድስ (ፍጥነቱን እንዳይቀንስብን)
    if now - last_edit < 8:
        return
    
    last_edit = now
    percent = (current / total) * 100
    # ለ Render ሰርቨር "እየሰራሁ ነው" የሚል ምልክት በሎግ ላይ ማሳየት
    print(f"DEBUG: {action} - {percent:.1f}%")
    
    try:
        await status.edit(f"🚀 **{action}**\n`[{'■' * int(percent//10)}{'□' * (10 - int(percent//10))}]` {percent:.1f}%")
    except:
        pass

# --- 4. THE HANDLER ---
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.is_private and "t.me/" in event.text:
        me = await client.get_me()
        if event.sender_id != me.id: return 

        status = await event.reply("⚡ **አልትራ ፈጣን ዳውንሎድ እየተጀመረ ነው...**")
        
        try:
            # ሊንክ አወጣጥ
            parts = event.text.split('/')
            msg_id = int(parts[-1])
            chat = int("-100" + parts[-2]) if "t.me/c/" in event.text else parts[-2]
            
            msg = await client.get_messages(chat, ids=msg_id)
            if not (msg and msg.media):
                return await status.edit("❌ ፋይል የለውም!")

            file_name = msg.file.name or f"file_{random.randint(100,999)}.mp4"
            
            # --- HIGH SPEED DOWNLOAD ---
            # 'request_size' እና 'part_size_kb' ለፈጣን ዳውንሎድ ይረዳሉ
            path = await client.download_media(
                msg,
                progress_callback=lambda c, t: fast_progress(c, t, status, "Downloading")
            )

            # --- HIGH SPEED UPLOAD ---
            await status.edit("📤 **ዳውንሎድ አልቋል፤ ወደ Saved Messages እየበረረ ነው...**")
            
            await client.send_file(
                'me', 
                path, 
                force_document=True,
                caption=f"✅ `{file_name}`",
                progress_callback=lambda c, t: fast_progress(c, t, status, "Uploading")
            )

            if os.path.exists(path): os.remove(path)
            await status.delete()

        except Exception as e:
            await status.edit(f"❌ ስህተት: {str(e)}")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    client.start()
    client.run_until_disconnected()
