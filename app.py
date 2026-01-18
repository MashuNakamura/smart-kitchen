import os
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_cors import CORS
from passlib.context import CryptContext
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import utils
import db_utils

# ==========================================
# SETUP & SECURITY CONFIGURATION
# ==========================================
app = Flask(__name__)

# NOTE : Change this in production to link deployed
CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5000", "http://localhost:5000"]}})

# Konfigurasi Secret Key untuk session
app.secret_key = os.environ.get("SECRET_KEY", "kelapasawit123!@#")

# Rate Limiting to Prevent Abuse
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Konfigurasi Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================================
# ERROR HANDLERS
# ==========================================
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error_code': 429,
        'success': False,
        'message': f'Too many try. Please try again later {e}'
    }), 429

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
@limiter.limit("5 per minute") # [Limit] Max 5x coba register per menit
def register():
    # Get JSON Data from Request
    data, error = utils.data_validate()
    if error: return error

    # User Data
    username = data.get("username")
    email    = data.get("email")
    password = data.get("password")

    # Validate Data
    if not username or not email or not password:
        return jsonify({
            'error_code': 1,
            'success': False,
            'message': 'Username and Password are required.'
        }), 400

    # Validate Email Format
    if not utils.email_format(email):
        return jsonify({
            'error_code': 2,
            'success': False,
            'message': 'Invalid email format.'
        })

    # Validate Password Strength
    if not utils.minimum_password(password):
        return jsonify({
            'error_code': 3,
            'success': False,
            'message': 'Password must be at least 8 characters long. 1 uppercase, 1 lowercase, 1 number.'
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
            'error_code': 4,
            'success': False,
            'message': result['message']
        }), 400

@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute") # [Limit] Max 10x coba login per menit
def login():
    # Get JSON Data from Request
    data, error = utils.data_validate()
    if error: return error

    # User Data
    identifier = data.get("identifier") # Bisa username atau email
    password   = data.get("password")

    # Validate Data
    if not identifier or not password:
        return jsonify({
            'error_code': 5,
            'success': False,
            'message': 'Identifier and Password are required.'
        }), 400

    # Check User in Database
    user = db_utils.check_user(identifier)

    if user and pwd_context.verify(password, user['password']):
        # Set Session
        session['user_id'] = user['id']
        session['username'] = user['username']

        return jsonify({
            'error_code': 0,
            'success': True,
            'message': f'Login successful. Welcome {user["username"]}!',
            'username': user['username']
        })
    else:
        return jsonify({
            'error_code': 6,
            'success': False,
            'message': 'Invalid identifier or password.'
        }), 401

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({
        'error_code': 0,
        'success': True,
        'message': 'Logged out successfully.'
    })

# ==========================================
# Core Recipe Generation
# ==========================================
@app.route('/api/generate', methods=['POST'])
@utils.auth_required
@limiter.limit("1 per 3 minute") # [Limit] Max 1x generate resep per 3 menit
def generate_recipe():
    # Get JSON Data from Request
    data, error = utils.data_validate()
    if error: return error

    # Bahan Input
    bahan = data.get("bahan")
    mode = data.get("mode", "normal")  # default mode is 'normal'

    # Validate Bahan
    if not bahan:
        return jsonify({
            'error_code': 7,
            'success': False,
            'message': 'Ingredient is required to generate recipe.'
        }), 400

    # Execute Recipe Generation
    try:
        # Call AI Utility to Generate Recipe
        resep_text = utils.generate_resep_final(bahan, mode)

        # Check if AI returned an error message
        if "Maaf" in resep_text and "kendala" in resep_text:
            return jsonify({
                'error_code': 8,
                'success': False,
                'message': 'AI failed to generate recipe. Try different ingredients.'
            }), 500

    except Exception as e:
        print(f"[AI ERROR] {e}")
        return jsonify({
            'error_code': 9,
            'success': False,
            'message': f'Server Error during generation: {str(e)}'
        }), 500

    # 5. SAVE TO DATABASE (History)
    try:
        user_id = session['user_id']
        history_id = db_utils.save_recipe_to_history(user_id, bahan, resep_text)

        return jsonify({
            'error_code': 0,
            'success': True,
            'message': 'Recipe generated successfully!',
            'data': {
                'history_id': history_id,
                'resep': resep_text,
                'mode': mode
            }
        })
    except Exception as e:
        return jsonify({
            'error_code': 10,
            'success': False,
            'message': f'Database Error: {str(e)}'
        }), 500

# ==========================================
# History and Favorites
# ==========================================
@app.route('/api/history', methods=['GET'])
@utils.auth_required
def get_history():
    try:
        # Ambil User ID dari Session
        user_id = session['user_id']

        history_list = db_utils.get_user_history(user_id)

        return jsonify({
            'error_code': 0,
            'success': True,
            'message': 'User history retrieved successfully.',
            'data': history_list
        })
    except Exception as e:
        return jsonify({
            'error_code': 11,
            'success': False,
            'message': f'Database Error: {str(e)}'
        }), 500

# Favorites are Optional
@app.route('/api/favorites', methods=['POST']) # Toggle Like
@utils.auth_required
def add_favorite():
    # Get JSON Data from Request
    data, error = utils.data_validate()
    if error: return error

    # Get History ID
    history_id = data.get("history_id")
    if not history_id:
        return jsonify({
            'error_code': 12,
            'success': False,
            'message': 'History ID is required to toggle favorite.'
        }), 400

    try:
        is_fav = db_utils.toggle_favorite(history_id)
        msg = "Added to favorites" if is_fav else "Removed from favorites"
        return jsonify({
            'error_code': 0,
            'success': True,
            'message': msg,
            'data': {
                'is_favorite': is_fav
            }
        })
    except Exception as e:
        return jsonify({
            'error_code': 13,
            'success': False,
            'message': f'Database Error: {str(e)}'
        }), 500

@app.route('/api/favorites', methods=['GET']) # List Favorites
@utils.auth_required
def get_favorites():
    # Get User ID from Session
    user_id = session['user_id']
    try:
        fav_list = db_utils.get_user_favorites(user_id)
        return jsonify({
            'error_code': 0,
            'success': True,
            'message': 'Favorites retrieved successfully.',
            'data': fav_list
        })
    except Exception as e:
        return jsonify({
            'error_code': 14,
            'success': False,
            'message': f'Database Error: {str(e)}'
        }), 500

# ==========================================
# Frontend Route
# ==========================================
@app.route('/')
def view_landing():
    if 'user_id' in session:
        return redirect(url_for('view_dashboard'))
    return render_template('index.html')

@app.route('/register')
def view_register():
    if 'user_id' in session:
        return redirect(url_for('view_dashboard'))
    return render_template('register.html')

@app.route('/login')
def view_login():
    if 'user_id' in session:
        return redirect(url_for('view_dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def view_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('view_login'))
    return render_template('dashboard.html')

@app.route('/history')
def view_history_page():
    if 'user_id' not in session:
        return redirect(url_for('view_login'))
    return render_template('history.html')

# ==========================================
# Run the Flask Application
# ==========================================
if __name__ == '__main__':
    print("Server is running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)