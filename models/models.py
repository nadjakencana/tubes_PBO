# models/models.py
import sqlite3
from dataclasses import dataclass

@dataclass
class TempatNongkrong:
    id: int
    nama: str
    jam_buka: str
    harga: str
    latitude: float
    longitude: float
    foto: str
    rating: float
    komentar: str
    creator: str  # Kolom ke-10

class DataManager:
    def __init__(self, db_path="database/app.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        # Periksa apakah kolom 'creator' sudah ada
        cursor.execute("PRAGMA table_info(tempat)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'creator' not in columns:
            # Jika belum ada, tambahkan kolom 'creator' ke tabel yang sudah ada
            cursor.execute("ALTER TABLE tempat ADD COLUMN creator TEXT DEFAULT ''")
        
        # Buat tabel jika belum ada (untuk instalasi pertama kali)
        cursor.execute('''CREATE TABLE IF NOT EXISTS tempat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            jam_buka TEXT,
            harga TEXT,
            latitude REAL,
            longitude REAL,
            foto TEXT,
            rating REAL,
            komentar TEXT,
            creator TEXT
        )''')
        self.conn.commit()

    def get_all_tempat(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nama, jam_buka, harga, latitude, longitude, foto, rating, komentar, creator FROM tempat")
        rows = cursor.fetchall()
        # Kode ini sekarang aman karena kita sudah memastikan kolom 'creator' selalu ada
        return [TempatNongkrong(*row) for row in rows]

    def tambah_tempat(self, t: TempatNongkrong, creator: str):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO tempat (nama, jam_buka, harga, latitude, longitude, foto, rating, komentar, creator)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (t.nama, t.jam_buka, t.harga, t.latitude, t.longitude, t.foto, t.rating, t.komentar, creator))
        self.conn.commit()

    def hapus_tempat(self, id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tempat WHERE id=?", (id,))
        self.conn.commit()

    def edit_tempat(self, t: TempatNongkrong):
        cursor = self.conn.cursor()
        # Pastikan kolom creator juga diupdate jika ada perubahan di masa depan
        cursor.execute("""UPDATE tempat SET nama=?, jam_buka=?, harga=?, latitude=?, longitude=?,
            foto=?, rating=?, komentar=? WHERE id=?""",
            (t.nama, t.jam_buka, t.harga, t.latitude, t.longitude, t.foto, t.rating, t.komentar, t.id))
        self.conn.commit()
