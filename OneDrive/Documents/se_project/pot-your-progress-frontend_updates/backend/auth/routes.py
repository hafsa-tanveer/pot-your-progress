from flask import Blueprint, request, jsonify, session
import oracledb
import bcrypt
import sys
import os

# Path fix to find db.py in parent folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db_connection

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

    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Database connection failed"}), 500
    
    cursor = conn.cursor()

    try:
        # 2. Save to DB (FLORA_APP schema)
        cursor.callproc("register_user", [full_name, email, hashed_password_str])
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201

    except oracledb.DatabaseError as e:
        error_obj, = e.args
        # ORA-20001 is defined in your SQL code for duplicates
        if error_obj.code == 20001: 
            return jsonify({"message": "Email already exists"}), 409
        else:
            return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# --------------------------------------------------------
#                  LOGIN ROUTE (ENCRYPTED CHECK)
# --------------------------------------------------------
@auth_bp.post("/login")
def login():
    data = request.json
    email = data.get("email") 
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Missing credentials"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = conn.cursor()

    try:
        # 1. Fetch Encrypted Hash
        ref_cursor = cursor.callfunc("get_user_by_email", oracledb.CURSOR, [email])
        user_row = ref_cursor.fetchone()

        if user_row:
            user_id = user_row[0]
            db_name = user_row[1]
            db_hash = user_row[2] # This is the bcrypt hash

            # 2. Verify Password
            if bcrypt.checkpw(password.encode('utf-8'), db_hash.encode('utf-8')):
                
                # 3. Create Session
                session['user_id'] = user_id
                session['user_name'] = db_name
                
                return jsonify({
                    "message": "Login successful",
                    "token": f"mock-jwt-token-{user_id}", 
                    "user": {"id": user_id, "name": db_name, "email": email}
                }), 200
            else:
                return jsonify({"message": "Invalid credentials"}), 401
        else:
            return jsonify({"message": "User not found"}), 401

    except oracledb.DatabaseError as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# --------------------------------------------------------
#                   LOGOUT ROUTE
# --------------------------------------------------------
@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200