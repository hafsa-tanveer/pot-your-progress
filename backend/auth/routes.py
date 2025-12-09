from flask import Blueprint, request, jsonify, session
import bcrypt
import sys
import os

# Path fix to find db.py in parent folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_supabase_client

auth_bp = Blueprint("auth", __name__)

# --------------------------------------------------------
#                 SIGNUP ROUTE (ENCRYPTED)
# --------------------------------------------------------
@auth_bp.post("/signup")
def signup():
    data = request.json
    full_name = data.get("name") 
    email = data.get("email")
    password = data.get("password")
    
    if not all([full_name, email, password]):
        return jsonify({"message": "Missing required fields"}), 400

    # 1. Encrypt Password (Bcrypt)
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_password_str = hashed_bytes.decode('utf-8')

    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500

    try:
        # 2. Save to Supabase
        response = supabase.table('users').insert({
            'full_name': full_name,
            'email': email,
            'password_hash': hashed_password_str
        }).execute()
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        error_str = str(e)
        # Check if it's a duplicate email error
        if 'duplicate' in error_str.lower() or 'unique' in error_str.lower() or 'already exists' in error_str.lower():
            return jsonify({"message": "Email already exists"}), 409
        else:
            return jsonify({"message": str(e)}), 500


# --------------------------------------------------------
#                  LOGIN ROUTE (ENCRYPTED CHECK)
# --------------------------------------------------------
@auth_bp.post("/login")
def login():
    data = request.json
    identifier = data.get("email")  # accept email or username in same field
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"message": "Missing credentials"}), 400

    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500

    try:
        # 1. Fetch User by Email OR Username (full_name)
        or_filter = f"email.eq.{identifier},full_name.eq.{identifier}"
        response = (
            supabase.table('users')
            .select('user_id, full_name, email, password_hash')
            .or_(or_filter)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            user_data = response.data[0]
            user_id = user_data['user_id']
            db_name = user_data['full_name']
            db_email = user_data['email']
            db_hash = user_data['password_hash']  # bcrypt hash

            # 2. Verify Password
            if bcrypt.checkpw(password.encode('utf-8'), db_hash.encode('utf-8')):
                
                # 3. Create Session
                session['user_id'] = user_id
                session['user_name'] = db_name
                
                return jsonify({
                    "message": "Login successful",
                    "token": f"mock-jwt-token-{user_id}", 
                    "user": {"id": user_id, "name": db_name, "email": db_email}
                }), 200
            else:
                return jsonify({"message": "Invalid credentials"}), 401
        else:
            return jsonify({"message": "User not found"}), 401

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --------------------------------------------------------
#                   LOGOUT ROUTE
# --------------------------------------------------------
@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200