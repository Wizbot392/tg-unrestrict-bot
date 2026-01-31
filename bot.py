import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Setup these in Koyeb Dashboard
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    if event.text and "t.me/" in event.text:
        status = await event.reply("☁️ Processing in Cloud...")
        try:
            # Download to cloud temp storage
            file = await event.download_media()
            # Send to your 'Saved Messages'
            await client.send_file('me', file, caption="✅ Unrestricted File")
            # Delete from cloud immediately (Zero storage used)
            if os.path.exists(file):
                os.remove(file)
            await status.edit("🚀 Sent to your Saved Messages!")
        except Exception as e:
            await status.edit(f"❌ Error: {e}")

print("Bot is running...")
client.start()
client.run_until_disconnected()
