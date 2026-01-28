from telethon import TelegramClient, events
import sqlite3, hashlib, os, asyncio

# =============== НАСТРОЙКИ ===============
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# ГРУППЫ КОТОРЫЕ СЛУШАЕМ (user-аккаунт может читать любые)
SOURCE_CHATS = [
    -1001235383010,
    -1001151684062,
    -1001250730941,
    -1001421793061,
    -1002285316560
]

# КУДА ПЕРЕСЫЛАЕМ
TARGET_CHAT = -1003323637756

KEYWORDS = ["италия", "италию"]
# ========================================

# ⚠️ ВАЖНО: имя должно совпадать с загруженным session-файлом
client = TelegramClient("italy_user_session", api_id, api_hash)


# ============ БАЗА ДАННЫХ ДЛЯ ДУБЛЕЙ ============
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
# =================================================


@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def handler(event):
    try:
        text = event.raw_text.lower()
    except:
        return

    print("📩 Новое сообщение:", event.chat_id, text)

    if any(word in text for word in KEYWORDS):
        text_hash = hash_text(text)

        if was_sent(text_hash):
            print("⏩ Уже пересылали, пропускаю")
            return

        try:
            await client.forward_messages(TARGET_CHAT, event.message)
            mark_sent(text_hash)
            print("✅ Переслано!")
        except Exception as e:
            print("⚠️ Ошибка пересылки:", e)


async def main():
    init_db()
    print("🟢 USERBOT запущен. Слушаю группы...")
    await client.start()  # ← БЕЗ bot_token
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())










