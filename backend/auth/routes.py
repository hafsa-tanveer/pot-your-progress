from flask import Blueprint, request, jsonify, session
import bcrypt
import sys
import os
import random
import string
from datetime import datetime, timedelta
import logging

# Path fix to find db.py in parent folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_supabase_client

auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)

# In-memory OTP storage (email -> {otp, expires_at})
# In production, consider using Redis or database table
otp_storage = {}

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

# --------------------------------------------------------
#              FORGET PASSWORD - SEND OTP
# --------------------------------------------------------
@auth_bp.post("/forget-password")
def forget_password():
    """
    Generates a 6-digit OTP and returns it to display on the website.
    """
    data = request.json
    email = data.get("email")
    
    if not email:
        return jsonify({"message": "Email is required"}), 400
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        # Check if user exists
        response = supabase.table('users').select('user_id, email, full_name').eq('email', email).execute()
        
        if not response.data or len(response.data) == 0:
            # Don't reveal if email exists or not (security best practice)
            return jsonify({"message": "If the email exists, an OTP has been sent"}), 200
        
        user_data = response.data[0]
        user_email = user_data['email']
        user_name = user_data['full_name']
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store OTP with expiration (10 minutes)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        otp_storage[user_email] = {
            'otp': otp,
            'expires_at': expires_at.isoformat(),
            'verified': False
        }
        
        # ====================================================================
        # RESEND EMAIL API CALL - COMMENTED OUT (Visible for review)
        # ====================================================================
        # Free tier email services don't allow sending without domain purchase
        # This code is kept for reference and can be uncommented once a domain is purchased
        # 
        # from email_service import send_otp_email
        # email_sent = send_otp_email(user_email, user_name, otp)
        # 
        # if email_sent:
        #     # Email sent successfully via Resend
        #     return jsonify({
        #         "message": "OTP has been sent to your email address. Please check your inbox."
        #     }), 200
        # else:
        #     # Fallback: Display OTP on website if email fails (for testing/debugging)
        #     logger.warning(f"Failed to send OTP email to {user_email}, displaying OTP in response")
        #     return jsonify({
        #         "message": f"Your OTP code is: {otp}. Please enter this code to verify.",
        #         "otp": otp  # Fallback if email fails
        #     }), 200
        # ====================================================================
        
        # Display OTP in popup (like error messages)
        return jsonify({
            "message": f"Your OTP code is: {otp}. Please enter this code to verify.",
            "otp": otp
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# --------------------------------------------------------
#              VERIFY OTP
# --------------------------------------------------------
@auth_bp.post("/verify-otp")
def verify_otp():
    """
    Verifies the OTP entered by the user.
    Returns a token/session that allows password reset.
    """
    data = request.json
    email = data.get("email")
    otp = data.get("otp")
    
    if not email or not otp:
        return jsonify({"message": "Email and OTP are required"}), 400
    
    # Check if OTP exists and is valid
    if email not in otp_storage:
        return jsonify({"message": "Invalid or expired OTP"}), 400
    
    otp_data = otp_storage[email]
    stored_otp = otp_data['otp']
    expires_at = datetime.fromisoformat(otp_data['expires_at'])
    
    # Check if OTP is expired
    if datetime.utcnow() > expires_at:
        del otp_storage[email]
        return jsonify({"message": "OTP has expired. Please request a new one"}), 400
    
    # Verify OTP
    if otp != stored_otp:
        return jsonify({"message": "Invalid OTP"}), 400
    
    # Mark OTP as verified and extend expiration for password reset (5 more minutes)
    otp_storage[email]['verified'] = True
    otp_storage[email]['expires_at'] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    
    # Store verification in session
    session['password_reset_email'] = email
    session['password_reset_verified'] = True
    
    return jsonify({
        "message": "OTP verified successfully",
        "verified": True
    }), 200

# --------------------------------------------------------
#              RESET PASSWORD (UPDATED)
# --------------------------------------------------------
@auth_bp.post("/reset-password")
def reset_password():
    """
    Resets the password after OTP verification.
    """
    data = request.json
    email = data.get("email")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")
    
    if not email or not new_password or not confirm_password:
        return jsonify({"message": "Email, new password, and confirm password are required"}), 400
    
    if new_password != confirm_password:
        return jsonify({"message": "Passwords do not match"}), 400
    
    # Check if OTP was verified
    if email not in otp_storage or not otp_storage[email].get('verified', False):
        return jsonify({"message": "Please verify OTP first"}), 400
    
    # Check if verification is still valid
    expires_at = datetime.fromisoformat(otp_storage[email]['expires_at'])
    if datetime.utcnow() > expires_at:
        del otp_storage[email]
        return jsonify({"message": "OTP verification expired. Please request a new one"}), 400
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        # Hash new password
        hashed_bytes = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_bytes.decode('utf-8')
        
        # Update password in database
        response = supabase.table('users').update({
            'password_hash': hashed_password_str
        }).eq('email', email).execute()
        
        if not response.data:
            return jsonify({"message": "User not found"}), 404
        
        # Clear OTP from storage
        del otp_storage[email]
        session.pop('password_reset_email', None)
        session.pop('password_reset_verified', None)
        
        return jsonify({"message": "Password has been reset successfully"}), 200
        
    except Exception as e:
        return jsonify({"message": f"Error resetting password: {str(e)}"}), 500