# ==========================================
# Library Imports
# ==========================================
import os
import re
import random
import string
import requests
from functools import wraps
from flask import request, jsonify, session

# ==========================================
# Configure Paths
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RESEP_PATH = os.path.join(BASE_DIR, 'data', 'Indonesian_Food_Recipes.csv')
DATA_NUTRISI_PATH = os.path.join(BASE_DIR, 'data', 'nutrition.csv')
MODEL_ADAPTER_PATH = os.path.join(BASE_DIR, 'models', 'model_chef_siap_pakai')

# Validasi Path (Safety Check)
if not BASE_DIR:
    raise ValueError("BASE_DIR tidak ditemukan.")
elif not DATA_RESEP_PATH:
    raise ValueError("DATA_RESEP_PATH tidak ditemukan.")
elif not DATA_NUTRISI_PATH:
    raise ValueError("DATA_NUTRISI_PATH tidak ditemukan.")
elif not MODEL_ADAPTER_PATH:
    raise ValueError("MODEL_ADAPTER_PATH tidak ditemukan.")

# ==========================================
# 1. Load Resources Function
# ==========================================
def load_resources():
    """
    Tugas: Memuat Model AI, Vector DB, dan Dataset ke RAM.
    Jalan sekali saja saat server start.
    """
    print("--- [UTILS] Skipping resource loading, handled by model server ---")
    pass

# ==========================================
# 4. Main Generator (Controller)
# ==========================================
def generate_resep_final(bahan_input, mode="normal"):
    """
    Tugas: Pipeline Utama (Load -> Retrieve -> Generate -> Clean).
    """
    api_key = os.environ.get("API_KEY")
    if not api_key:
        return "Maaf, API key untuk model server tidak ditemukan."

    model_server_url = os.environ.get("MODEL_SERVER_URL")
    if not model_server_url:
        return "Maaf, URL model server tidak ditemukan."

    try:
        headers = {
            "X-API-Key": api_key
        }
        response = requests.post(f"{model_server_url}/api/generate", json={"bahan": bahan_input, "mode": mode}, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        if data.get("success"):
            return data.get("data", {}).get("resep", "Maaf, terjadi kesalahan saat memproses resep.")
        else:
            return data.get("message", "Maaf, terjadi kesalahan saat memproses resep.")
    except requests.exceptions.RequestException as e:
        print(f"[ERR] Error calling model server: {e}")
        return "Maaf, dapur sedang kendala teknis."

# ==========================================
# Helper: Validation Functions
# ==========================================
def email_format(email):
    """
    Tugas: Validasi format email sederhana menggunakan Regex.
    """
    if not email: return False
    # Pattern standar email
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def minimum_password(password):
    """
    Tugas: Validasi kekuatan password.
    Aturan: Minimal 8 karakter, ada huruf besar, huruf kecil, dan angka.
    """
    if not password: return False
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password): # Huruf Besar
        return False
    if not re.search(r'[a-z]', password): # Huruf Kecil
        return False
    if not re.search(r'[0-9]', password): # Angka
        return False
    return True

def data_validate():
    """
    Otomatis ambil JSON. Kalau kosong, return error response.
    Cara pakai: data, error = utils.get_json_input()
    """
    data = request.get_json()
    if not data:
        return None, (jsonify({
            'error_code': 400,
            'success': False,
            'message': 'Invalid JSON data.'
        }), 400)

    return data, None

def auth_required(f):
    """
    Decorator: Cek apakah user sudah login (session).
    Cara pakai: @utils.auth_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Cek session
        if 'user_id' not in session:
            return jsonify({
                'error_code': 401,
                'success': False,
                'message': 'Authentication required. Please log in.'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def generate_otp(length=6):
    """
    Tugas: Generate OTP code (numeric only).
    """
    return ''.join(random.choices(string.digits, k=length))
