import random
import string
import os
import sqlite3
from telethon import TelegramClient
from config import sessions_folder

if not os.path.exists(sessions_folder):
    os.makedirs(sessions_folder)

session_name = ''.join(random.choices(string.ascii_lowercase, k=16))


api_id = int(input("API ID: "))
api_hash = input("API HASH: ")

session_path = os.path.join(sessions_folder, session_name)

client = TelegramClient(session_path, api_id=api_id, api_hash=api_hash)

async def main():
    await client.start()
    print(f"\nСессия {session_name} успешно создана.\n")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO api (api_id, api_hash, session) VALUES (?, ?, ?)", (api_id, api_hash, session_name))
    conn.commit()
    conn.close()

with client:
    
    client.loop.run_until_complete(main())