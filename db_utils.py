# ==========================================
# Import Modules
# ==========================================
import os
import sqlite3
import math

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
    Tugas: Membuat tabel SQL asli dengan constraint UNIQUE.
    """
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        print(f"[DB] Folder '{DB_FOLDER}' created.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users (
                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        username TEXT NOT NULL UNIQUE,
                                                        email TEXT NOT NULL UNIQUE,
                                                        password TEXT NOT NULL
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS history (
                                                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                          user_id INTEGER NOT NULL,
                                                          input_bahan TEXT NOT NULL,
                                                          resep_text TEXT NOT NULL,
                                                          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                                                          is_favorite INTEGER DEFAULT 0,
                                                          FOREIGN KEY (user_id) REFERENCES users(id)
                       )
                   ''')

    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {DB_PATH}.")

# ==========================================
# 2. User Authentication (Auth)
# ==========================================
def add_user(username, email, password_hash):
    """
    Tugas: Insert user baru ke SQLite
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
                       INSERT INTO users (username, email, password)
                       VALUES (?, ?, ?)
                       ''', (username, email, password_hash))

        conn.commit()
        conn.close()

        return {
            'error_code': 0,
            'success': True,
            'message': f'User {username} registered successfully.'
        }

    except sqlite3.IntegrityError:
        if 'conn' in locals(): conn.close()
        return {
            'error_code': 1,
            'success': False,
            'message': f'Username or Email already exists.'
        }

    except Exception as e:
        if 'conn' in locals(): conn.close()
        return {
            'error_code': 2,
            'success': False,
            'message': f'Error: {str(e)}'
        }

def check_user(identifier):
    """
    Tugas: Mencari user berdasarkan username ATAU email (Untuk Login).
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT * FROM users WHERE username = ? OR email = ?
                       ''', (identifier, identifier))

        user = cursor.fetchone()
        conn.close()

        if user:
            return dict(user)
        return None

    except Exception as e:
        print(f"DB Error: {e}")
        return None

# ==========================================
# 3. Core Features (History & Cache)
# ==========================================
def save_recipe_to_history(user_id, bahan, resep_text):
    """
    Tugas: Menyimpan hasil generate AI ke tabel history.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
                       INSERT INTO history (user_id, input_bahan, resep_text)
                       VALUES (?, ?, ?)
                       ''', (user_id, bahan, resep_text))

        # Ambil ID dari data yang baru aja masuk
        new_id = cursor.lastrowid

        conn.commit()
        conn.close()

        print(f"[DB] Saved history ID: {new_id} for User: {user_id}")
        return new_id

    except Exception as e:
        print(f"[DB Error] Save History: {e}")
        return None

def get_user_history(user_id, search_query=None, start_date=None, end_date=None, page=1, per_page=6):
    """
    Tugas: Mengambil daftar riwayat masak user (urut dari yang terbaru).
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Bangun Bagian WHERE (Filter)
        where_clause = "WHERE user_id = ?"
        params = [user_id]

        if search_query:
            where_clause += " AND (input_bahan LIKE ? OR resep_text LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        # Cek Start Date saja (Filter "Sejak Tanggal X")
        if start_date:
            where_clause += " AND created_at >= ?"
            params.append(f"{start_date} 00:00:00")

        # Cek End Date saja (Filter "Sampai Tanggal Y")
        if end_date:
            where_clause += " AND created_at <= ?"
            params.append(f"{end_date} 23:59:59")

        # 2. Hitung TOTAL DATA (Tanpa Limit)
        count_query = f"SELECT COUNT(*) FROM history {where_clause}"
        cursor.execute(count_query, params)
        total_items = cursor.fetchone()[0]

        # 3. Ambil DATA HALAMAN INI (Pakai Limit & Offset)
        # Offset = (Halaman - 1) * Jumlah per halaman
        offset = (page - 1) * per_page

        data_query = f"SELECT * FROM history {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        data_params = params + [per_page, offset]

        cursor.execute(data_query, data_params)
        rows = cursor.fetchall()
        conn.close()

        # Hitung Total Halaman
        total_pages = math.ceil(total_items / per_page)

        return {
            'data': [dict(row) for row in rows],
            'meta': {
                'total_items': total_items,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page
            }
        }

    except Exception as e:
        print(f"[DB Error] Get History: {e}")
        return {'data': [], 'meta': {'total_items': 0, 'total_pages': 0, 'current_page': 1, 'per_page': 6}}

# ==========================================
# 4. Optional Features (Favorites)
# ==========================================
def toggle_favorite(history_id):
    """
    Tugas: Mengubah status favorit (Like/Unlike).
    Return: Status Baru (True/False)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Cek status sekarang
        cursor.execute('SELECT is_favorite FROM history WHERE id = ?', (history_id,))
        current = cursor.fetchone()

        if not current:
            conn.close()
            return False

        # 2. Balik statusnya (0 jadi 1, 1 jadi 0)
        current_status = current[0]
        new_status = 1 if current_status == 0 else 0

        # 3. Update database
        cursor.execute('UPDATE history SET is_favorite = ? WHERE id = ?', (new_status, history_id))

        conn.commit()
        conn.close()

        print(f"[DB] Toggled Favorite ID {history_id} to {new_status}")
        return new_status == 1 # Return True kalau jadi favorit

    except Exception as e:
        print(f"[DB Error] Toggle Favorite: {e}")
        return False

def get_user_favorites(user_id, search_query=None, start_date=None, end_date=None, page=1, per_page=6):
    """
    Tugas: Mengambil history yang dilike saja (is_favorite = 1).
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Create some Main Filter
        where_clause = ["user_id = ? AND is_favorite = 1"]
        params = [user_id]

        if search_query:
            where_clause.append("(input_bahan LIKE ? OR resep_text LIKE ?)")
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        # Cek Start Date saja (Filter "Sejak Tanggal X")
        if start_date:
            where_clause.append("created_at >= ?")
            params.append(f"{start_date} 00:00:00")

        # Cek End Date saja (Filter "Sampai Tanggal Y")
        if end_date:
            where_clause.append("created_at <= ?")
            params.append(f"{end_date} 23:59:59")

        # Gabung semua kondisi WHERE
        full_where_clause = " WHERE " + " AND ".join(where_clause)

        # 2. Hitung TOTAL DATA (Tanpa Limit)
        count_query = f"SELECT COUNT(*) FROM history {full_where_clause}"
        cursor.execute(count_query, params)
        total_items = cursor.fetchone()[0]

        # 3. Ambil DATA HALAMAN INI (Pakai Limit & Offset)
        # Offset = (Halaman - 1) * Jumlah per halaman
        offset = (page - 1) * per_page
        data_query = f"SELECT * FROM history {full_where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?"

        data_params = params + [per_page, offset]

        cursor.execute(data_query, data_params)
        rows = cursor.fetchall()
        conn.close()

        # Hitung Total Halaman
        total_pages = math.ceil(total_items / per_page)

        return {
            'data': [dict(row) for row in rows],
            'meta': {
                'total_items': total_items,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page
            }
        }

    except Exception as e:
        print(f"[DB Error] Get Favorites: {e}")
        return {'data': [], 'meta': {'total_items': 0, 'total_pages': 0, 'current_page': 1, 'per_page': 6}}

# ==========================================
# 5. Delete History Entry
# ==========================================
def delete_history_item(history_id):
    """
    Tugas: Menghapus entry history berdasarkan ID.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM history WHERE id = ?', (history_id,))

        conn.commit()
        conn.close()

        print(f"[DB] Deleted History ID: {history_id}")
    except Exception as e:
        print(f"[DB Error] Delete History: {e}")
        return False

# ==========================================
# 6. User Profile Management
# ==========================================
def get_user_by_id(user_id):
    """
    Tugas: Mengambil data user berdasarkan ID.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return dict(user)
        return None
    except Exception as e:
        print(f"[DB Error] Get User by ID: {e}")
        return None

def update_username(user_id, new_username):
    """
    Tugas: Mengupdate username user.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check availability
        cursor.execute("SELECT id FROM users WHERE username = ?", (new_username,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return False, "Username already taken."

        cursor.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
        conn.commit()
        conn.close()

        return True, "Username updated successfully."
    except Exception as e:
        print(f"[DB Error] Update Username: {e}")
        return False, str(e)

def update_password(user_id, new_password_hash):
    """
    Tugas: Mengupdate password user.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password_hash, user_id))
        conn.commit()
        conn.close()

        return True, "Password updated successfully."
    except Exception as e:
        print(f"[DB Error] Update Password: {e}")
        return False, str(e)

# ==========================================
# TEST AREA (Run this file directly to test)
# ==========================================
if __name__ == '__main__':
    print("--- MULAI TEST DATABASE ---")

    # Init Database
    init_db()

    # Test Cases
    # 1. Coba Register (Tambah User)
    test_result = add_user("tester_awal", "test@gmail.com", "hash_rahasia")
    print(f"Test Register: {test_result}")

    # 2. Coba Login (Cek User)
    user = check_user("tester_awal")
    if user:
        print(f"Test Login: Ketemu user ID {user['id']} - {user['username']}")
    else:
        print("Test Login: Gagal (User tidak ditemukan)")

    print("--- TEST SELESAI ---")