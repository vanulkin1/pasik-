import os
import sqlite3
from config import sessions_folder


api_id = input("Укажите общий api_id от всех сессий: ")
api_hash = input("Укажите общий api_hash от всех сессий: ")


conn = sqlite3.connect('')
cursor = conn.cursor()

for filename in os.listdir(sessions_folder):
    if filename.endswith(".session"):
        name = os.path.splitext(filename)[0]


        
        cursor.execute("INSERT INTO api (api_id, api_hash, session) VALUES (?, ?, ?)", (str(api_id), str(api_hash), str(name)))

conn.commit()
conn.close()