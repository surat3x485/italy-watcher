from telethon import TelegramClient, events
import sqlite3, hashlib, os, asyncio

# =============== НАСТРОЙКИ ===============
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

SOURCE_CHATS = [
    -1001235383010,
    -1001151684062,
    -1001250730941,
    -1001421793061,
    -1002285316560
]

TARGET_CHAT = -1003323637756
KEYWORDS = ["италия", "италию"]
# ========================================

client = TelegramClient("italy_user_session", api_id, api_hash)

# ===== База анти-дублей =====
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

# ===== СЛУШАЕМ СООБЩЕНИЯ =====
@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def handler(event):
    print("MESSAGE FROM:", event.chat_id, event.raw_text)

    text = (event.raw_text or "").lower()

    if any(word in text for word in KEYWORDS):
        text_hash = hash_text(text)

        if was_sent(text_hash):
            print("⏩ Уже было, пропускаю...")
            return

        try:
            await client.forward_messages(TARGET_CHAT, event.message)
            mark_sent(text_hash)
            print("✅ Переслано!")
        except Exception as e:
            print("⚠️ Ошибка пересылки:", e)

# ===== ЗАПУСК =====
async def main():
    init_db()
    print("Userbot запущен. Слушаю группы...")
    await client.start()   # ← ВАЖНО: БЕЗ bot_token
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())









