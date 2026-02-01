# ==========================================
# Library Imports
# ==========================================
import os
import re
import random
import string
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

def send_otp_email(email, otp_code):
    """
    Tugas: Mengirim OTP via email menggunakan Gmail SMTP.
    Return: True jika berhasil, False jika gagal.
    """
    try:
        # Get email configuration from environment variables
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        smtp_from_email = os.environ.get('SMTP_FROM_EMAIL', smtp_username)
        
        # Validate configuration
        if not smtp_username or not smtp_password:
            print("[EMAIL] SMTP credentials not configured. Skipping email send.")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Kode OTP Verifikasi - SmartKitchen'
        msg['From'] = smtp_from_email
        msg['To'] = email
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f97316; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 5px 5px; }}
                .otp-box {{ background-color: white; border: 2px solid #f97316; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; margin: 20px 0; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🍳 SmartKitchen</h1>
                </div>
                <div class="content">
                    <h2>Kode OTP Verifikasi</h2>
                    <p>Terima kasih telah mendaftar di SmartKitchen!</p>
                    <p>Gunakan kode OTP berikut untuk menyelesaikan pendaftaran akun Anda:</p>
                    <div class="otp-box">{otp_code}</div>
                    <p><strong>Kode ini berlaku selama 10 menit.</strong></p>
                    <p>Jika Anda tidak merasa mendaftar di SmartKitchen, abaikan email ini.</p>
                </div>
                <div class="footer">
                    <p>© 2026 SmartKitchen AI - Final Project</p>
                    <p>Email ini dikirim secara otomatis, mohon tidak membalas.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text alternative
        text_content = f"""
        SmartKitchen - Kode OTP Verifikasi
        
        Terima kasih telah mendaftar di SmartKitchen!
        
        Gunakan kode OTP berikut untuk menyelesaikan pendaftaran akun Anda:
        
        {otp_code}
        
        Kode ini berlaku selama 10 menit.
        
        Jika Anda tidak merasa mendaftar di SmartKitchen, abaikan email ini.
        
        © 2026 SmartKitchen AI - Final Project
        """
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"[EMAIL] OTP sent successfully to {email}")
        return True
        
    except Exception as e:
        print(f"[EMAIL] Failed to send OTP email: {e}")
        return False
