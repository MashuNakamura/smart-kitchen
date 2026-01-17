import os
import sqlite3
from datetime import datetime

# ==========================================
# Database Configuration
# ==========================================
DB_FOLDER = 'db'
DB_NAME = 'data.db'
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

# ==========================================
# 1. Initialization
# ==========================================
def init_db():
    """
    Tugas: Membuat folder db/ dan tabel-tabel SQL jika belum ada.
    Dipanggil saat server start.
    """
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        print(f"[DB] Folder '{DB_FOLDER}' created.")

    print(f"[DB] Initializing database at {DB_PATH} (WIP Mode)...")

    # TODO: Create Table 'users' (id, username, password_hash)
    # TODO: Create Table 'history' (id, user_id, input_bahan, resep_text, created_at, is_favorite)

    print("[DB] Tables ready (Simulated).")

    # ==========================================
# 2. User Authentication (Auth)
# ==========================================
def add_user(username, password):
    """
    Tugas: Register user baru ke database.
    """
    print(f"[DB] Registering user: {username} (WIP)")

    # TODO: Hash password
    # TODO: Insert ke table users

    # Return dummy success
    return {'success': True, 'msg': 'User registered successfully (Dummy)'}

def check_user(username, password):
    """
    Tugas: Validasi login user.
    """
    print(f"[DB] Checking login for: {username} (WIP)")

    # TODO: Select from users where username = ...
    # TODO: Verify password hash

    # Dummy Login Logic: Admin selalu bisa masuk
    if username == "admin" and password == "admin":
        return {'id': 1, 'username': 'admin'}

    return None

# ==========================================
# 3. Core Features (History & Cache)
# ==========================================
def save_recipe_to_history(user_id, bahan, resep_text):
    """
    Tugas: Menyimpan hasil generate AI ke database (sebagai cache & history).
    """
    print(f"[DB] Saving recipe for User {user_id}: '{bahan}'")

    # TODO: Insert into history

    return 101 # Return dummy history_id

def get_user_history(user_id):
    """
    Tugas: Mengambil daftar riwayat masak user.
    """
    # TODO: Select * from history where user_id = ... order by date desc

    # Dummy Data
    return [
        {
            'id': 101,
            'tanggal': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'bahan': 'Ayam, Tahu',
            'resep': 'Resep Ayam Tahu Spesial (Preview)...',
            'is_favorite': 0
        },
        {
            'id': 102,
            'tanggal': '2024-01-20 10:00',
            'bahan': 'Telur, Kecap',
            'resep': 'Telur Ceplok Kecap (Preview)...',
            'is_favorite': 1
        }
    ]

# ==========================================
# 4. Optional Features (Favorites)
# ==========================================
def toggle_favorite(history_id):
    """
    Tugas: Mengubah status favorit (Like/Unlike).
    """
    print(f"[DB] Toggling favorite for History ID {history_id}")

    # TODO: Update history set is_favorite = NOT is_favorite where id = ...

    return True # Anggap sekarang jadi favorit

def get_user_favorites(user_id):
    """
    Tugas: Mengambil history yang dilike saja.
    """
    # TODO: Select * from history where user_id = ... AND is_favorite = 1

    # Dummy Data
    return [
        {
            'id': 102,
            'tanggal': '2024-01-20 10:00',
            'bahan': 'Telur, Kecap',
            'resep': 'Telur Ceplok Kecap...',
            'is_favorite': 1
        }
    ]