from telethon import TelegramClient, events
import sqlite3, hashlib, time

# =============== НАСТРОЙКИ ===============
api_id = 25688901
api_hash = "bce76d30a9fede444bc9babc7d670347"
SOURCE_CHAT = "@TutGruz"
TARGET_CHAT = "https://t.me/+gabNeMUwv-plNDhi"
KEYWORDS = ["италия", "италию"]
# ========================================

client = TelegramClient("italy_watcher_session", api_id, api_hash)

# База данных для защиты от дублей
def init_db():
    conn = sqlite3.connect("sent.db")
    conn.execute("CREATE TABLE IF NOT EXISTS sent (hash TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

def was_sent(text_hash):
    conn = sqlite3.connect("sent.db")
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM sent WHERE hash = ?", (text_hash,))
    exists = cur.fetchone()
    conn.close()
    return exists is not None

def mark_sent(text_hash):
    conn = sqlite3.connect("sent.db")
    conn.execute("INSERT OR IGNORE INTO sent (hash) VALUES (?)", (text_hash,))
    conn.commit()
    conn.close()

def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

@client.on(events.NewMessage())
async def handler(event):
    text = event.raw_text.lower()
    if any(word in text for word in KEYWORDS):
        text_hash = hash_text(text)
        if was_sent(text_hash):
            print("⏩ Уже было, пропускаю...")
            return
        try:
            await client.forward_messages(TARGET_CHAT, event.message)
            mark_sent(text_hash)
            print("✅ Новое сообщение переслано!")
        except Exception as e:
            print("⚠️ Ошибка пересылки:", e)

async def main():
    init_db()
    print("Bot zapushen. Slushaet gruppu...")
    await client.start()
    await client.run_until_disconnected()

import asyncio
asyncio.run(main())
