from flask import Flask, jsonify, request, render_template, session
from flask_cors import CORS
from passlib.context import CryptContext
import utils
import db_utils

# Setup Flask application
app = Flask(__name__)
CORS(app)

# Konfigurasi Secret Key untuk session
app.secret_key = "sangat_rahasia_12345"

# Konfigurasi Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================================
# Initialize AI Model and Database
# ==========================================
print("[APP] Starting AI & Database...")

try:
    # 1. Load Model AI to RAM
    utils.load_resources()

    # 2. Initialize Database
    db_utils.init_db()

    print("[APP] Server Ready...")
except Exception as e:
    print(f"[APP] Failed to Start the Server: {e}")

# ==========================================
# AUTH ROUTES (Login & Register)
# ==========================================
@app.route('/api/register', methods=['POST'])
def register():
    # Get JSON Data from Request
    data = request.get_json()
    if not data:
        return jsonify({
            'error_code': 1,
            'success': False,
            'msg': 'Invalid JSON data.'
        }), 400

    # User Data
    username = data["username"]
    email    = data["email"]
    password = data["password"]

    # Validate Data
    if not username or not email or not password:
        return jsonify({
            'error_code': 2,
            'success': False,
            'message': 'Username and Password are required.'
        }), 400

    # Validate Email Format
    if not utils.email_format(email):
        return jsonify({
            'error_code': 3,
            'success': False,
            'message': 'Invalid email format.'
        })

    # Validate Password Strength
    if not utils.minimum_password(password):
        return jsonify({
            'error_code': 4,
            'success': False,
            'message': 'Password terlalu lemah. Minimal 8 karakter, harus ada Huruf Besar, Kecil, Angka, dan Simbol.'
        })

    # Hash Password
    hashed_password = pwd_context.hash(password)

    # Send Data
    result = db_utils.add_user(username, email, hashed_password)

    if result['success']:
        return jsonify({
            'error_code': 0,
            'success': True,
            'message': 'User registered successfully.'
        })
    else:
        return jsonify({
            'error_code': 5,
            'success': False,
            'message': result['msg']
        }), 400

@app.route('/api/login', methods=['POST'])
def login():
    return "WIP: Login Endpoint"

# ==========================================
# Core Recipe Generation
# ==========================================
@app.route('/api/generate', methods=['POST'])
def generate_recipe():
    return "WIP: Generate Recipe Endpoint"

# ==========================================
# History and Favorites
# ==========================================
@app.route('/api/history', methods=['GET'])
def get_history():
    return "WIP: Get History Endpoint"

# Favorites are Optional
@app.route('/api/favorites', methods=['POST']) # Toggle Like
def add_favorite():
    return "WIP: Toggle Favorite Endpoint"

@app.route('/api/favorites', methods=['GET']) # List Favorites
def get_favorites():
    return "WIP: Get Favorites Endpoint"

# ==========================================
# Frontend Route
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

# ==========================================
# Run the Flask Application
# ==========================================
if __name__ == '__main__':
    print("Server is running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)