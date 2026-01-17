from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import utils
import db_utils

# Setup Flask application
app = Flask(__name__)
CORS(app)

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
    return "WIP: Register Endpoint"

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