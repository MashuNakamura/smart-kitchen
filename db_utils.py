import os
import sqlite3

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

def get_user_history(user_id):
    """
    Tugas: Mengambil daftar riwayat masak user (urut dari yang terbaru).
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT * FROM history
                       WHERE user_id = ?
                       ORDER BY created_at DESC
                       ''', (user_id,))

        rows = cursor.fetchall()
        conn.close()

        # Convert list of rows to list of dicts
        return [dict(row) for row in rows]

    except Exception as e:
        print(f"[DB Error] Get History: {e}")
        return []

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

def get_user_favorites(user_id):
    """
    Tugas: Mengambil history yang dilike saja (is_favorite = 1).
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT * FROM history
                       WHERE user_id = ? AND is_favorite = 1
                       ORDER BY created_at DESC
                       ''', (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"[DB Error] Get Favorites: {e}")
        return []

# ==========================================
# TEST AREA
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