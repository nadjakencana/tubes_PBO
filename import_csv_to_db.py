# import_csv_to_db.py
import pandas as pd
import sqlite3

df = pd.read_csv("data/nongkrong_tembalang.csv")

conn = sqlite3.connect("database/app.db")
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO tempat (nama, jam_buka, harga, latitude, longitude, foto, rating, komentar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (row["Nama"], row["Jam Buka"], row["Harga"], row["Latitude"], row["Longitude"],
         row["Foto"], row["Rating"], row["Komentar"])
    )

conn.commit()
conn.close()
print("✅ Data berhasil dimasukkan ke SQLite.")
