# ==========================================
# IMPORT MODULES
# ==========================================
import os
import math
from flask import Flask, jsonify, request, render_template, session, redirect, url_for

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
# AUTH ROUTES (Login & Register & Logout)
# ==========================================
@app.route('/api/request-otp', methods=['POST'])
@limiter.limit("3 per minute") # [Limit] Max 3x request OTP per menit
def request_otp():
    # Get JSON Data from Request
    data, error = utils.data_validate()
    if error: return error

    # User Data
    email = data.get("email")

    # Validate Data
    if not email:
        return jsonify({
            'error_code': 1,
            'success': False,
            'message': 'Email is required.'
        }), 400

    # Validate Email Format
    if not utils.email_format(email):
        return jsonify({
            'error_code': 2,
            'success': False,
            'message': 'Invalid email format.'
        }), 400

    # Check if email already exists
    existing_user = db_utils.check_user(email)
    if existing_user:
        return jsonify({
            'error_code': 4,
            'success': False,
            'message': 'Email already registered.'
        }), 400

    # Generate OTP
    otp_code = utils.generate_otp()

    # Save OTP to database
    if db_utils.create_otp(email, otp_code, expiry_minutes=10):
        # In production, send OTP via email
        # For now, we'll log it (in development)
        print(f"[OTP] Generated OTP for {email}: {otp_code}")
        
        # Build response
        response_data = {
            'error_code': 0,
            'success': True,
            'message': 'OTP sent successfully. Please check your email.'
        }
        
        # Only include OTP in response in development mode
        if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('DEBUG') == 'true':
            response_data['otp'] = otp_code  # Development only
        
        return jsonify(response_data)
    else:
        return jsonify({
            'error_code': 5,
            'success': False,
            'message': 'Failed to generate OTP. Please try again.'
        }), 500

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
    otp_code = data.get("otp")

    # Validate Data
    if not username or not email or not password or not otp_code:
        return jsonify({
            'error_code': 1,
            'success': False,
            'message': 'Username, Email, Password, and OTP are required.'
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

    # Verify OTP
    if not db_utils.verify_otp(email, otp_code):
        return jsonify({
            'error_code': 6,
            'success': False,
            'message': 'Invalid or expired OTP code.'
        }), 400

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
@limiter.limit("1 per minute") # [Limit] Max 1x generate resep per 3 menit
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
@limiter.exempt
def get_history():
    try:
        # Ambil User ID dari Session
        user_id = session['user_id']

        # Ambil parameter dari URL query string
        search = request.args.get('search', '')
        start_date = request.args.get('start', '')
        end_date = request.args.get('end', '')

        # Ambil parameter Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 6))

        # Panggil fungsi DB baru
        result = db_utils.get_user_history(user_id, search, start_date, end_date, page, per_page)
        return jsonify({
            'error_code': 0,
            'success': True,
            'message': 'User history retrieved successfully.',
            'data': result['data'],
            'meta': result['meta'],
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
@limiter.exempt
def get_favorites():
    try:
        # Get User ID from Session
        user_id = session['user_id']

        # Ambil parameter dari URL query string
        search = request.args.get('search', '')
        start_date = request.args.get('start', '')
        end_date = request.args.get('end', '')

        # Ambil parameter Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 6))

        fav_list = db_utils.get_user_favorites(user_id, search, start_date, end_date, page, per_page)
        return jsonify({
            'error_code': 0,
            'success': True,
            'message': 'Favorites retrieved successfully.',
            'data': fav_list['data'],
            'meta': fav_list['meta']
        })
    except Exception as e:
        return jsonify({
            'error_code': 14,
            'success': False,
            'message': f'Database Error: {str(e)}'
        }), 500

# ==========================================
# Delete History Item
# ==========================================
@app.route('/api/history/<int:history_id>', methods=['DELETE'])
@utils.auth_required
def delete_history_item(history_id):
    try:
        if history_id:
            db_utils.delete_history_item(history_id)
            return jsonify({
                'error_code': 0,
                'success': True,
                'message': 'History item deleted successfully.'
            })
        else:
            return jsonify({
                'error_code': 16,
                'success': False,
                'message': 'History ID is required to delete item.'
            }), 400
    except Exception as e:
        return jsonify({
            'error_code': 15,
            'success': False,
            'message': f'Database Error: {str(e)}'
        }), 500

# ==========================================
# 6. Profile Management Routes (User)
# ==========================================
@app.route('/profile')
@utils.auth_required
def profile_page():
    return render_template('profile.html')

@app.route('/api/profile/update-username', methods=['POST'])
@utils.auth_required
@limiter.limit("5 per minute")
def update_username_api():
    # 1. Get Data
    data, error = utils.data_validate()
    if error: return error
    
    new_username = data.get("new_username")
    user_id = session.get("user_id")

    if not new_username:
        return jsonify({'success': False, 'message': 'Username baru diperlukan.'}), 400

    # 2. Update DB
    success, msg = db_utils.update_username(user_id, new_username)

    if success:
        session['username'] = new_username # Update session
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'success': False, 'message': msg}), 400

@app.route('/api/profile/update-password', methods=['POST'])
@utils.auth_required
@limiter.limit("3 per minute")
def update_password_api():
    # 1. Get Data
    data, error = utils.data_validate()
    if error: return error

    old_password = data.get("old_password")
    new_password = data.get("new_password")
    user_id = session.get("user_id")

    if not old_password or not new_password:
        return jsonify({'success': False, 'message': 'Semua field harus diisi.'}), 400

    # 2. Validate Password Formatting
    if not utils.minimum_password(new_password):
        return jsonify({
            'success': False,
            'message': 'Password baru minimal 8 karakter, ada huruf besar, kecil, dan angka.'
        }), 400

    # 3. Get User Data to Verify Old Password
    user = db_utils.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User tidak ditemukan.'}), 404
    
    # 4. Verify Old Password
    if not pwd_context.verify(old_password, user['password']):
        return jsonify({'success': False, 'message': 'Password lama salah.'}), 401

    # 5. Hash New Password & Update
    hashed_new_password = pwd_context.hash(new_password)
    success, msg = db_utils.update_password(user_id, hashed_new_password)

    if success:
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'success': False, 'message': msg}), 500

# ==========================================
# Frontend Route
# ==========================================
@app.route('/')
def view_landing():
    # Login atau tidak Login tetap bisa akses halaman ini
    is_logged_in = 'user_id' in session
    return render_template('index.html', is_logged_in=is_logged_in)

@app.route('/register')
def view_register():
    # Redirect to dashboard if already logged in
    if 'user_id' in session:
        return redirect(url_for('view_dashboard'))
    return render_template('register.html')
    # return render_template('login.html')

@app.route('/login')
def view_login():
    # Redirect to dashboard if already logged in
    if 'user_id' in session:
        return redirect(url_for('view_dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def view_dashboard():
    # Protect route, redirect to login if not logged in
    if 'user_id' not in session:
        return redirect(url_for('view_login'))
    model_server_url = os.environ.get("MODEL_SERVER_URL", "http://localhost:5001")
    return render_template('dashboard.html', model_server_url=model_server_url)

@app.route('/history')
def view_history_page():
    # Protect route, redirect to login if not logged in
    if 'user_id' not in session:
        return redirect(url_for('view_login'))
    return render_template('history.html')

# ==========================================
# Run the Flask Application
# ==========================================
if __name__ == '__main__':
    print("Server is running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
