from flask import Blueprint, request, jsonify, session
from supabase import create_client
import os
import bcrypt

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

auth_bp = Blueprint("auth", __name__)

# ------------------ SIGNUP ------------------
@auth_bp.post("/signup")
def signup():
    data = request.json or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"message": "Missing required fields"}), 400

    try:
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Attempt to insert
        supabase.table("users").insert({
            "full_name": name,
            "email": email,
            "password_hash": hashed_password
        }).execute()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        # Check if it's a unique constraint violation
        err_str = str(e)
        if "duplicate key value violates unique constraint" in err_str or "already exists" in err_str:
            return jsonify({"message": "Email already exists"}), 409
        return jsonify({"message": str(e)}), 500


# ------------------ LOGIN ------------------
@auth_bp.post("/login")
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Missing credentials"}), 400

    try:
        # Fetch user by email
        res = supabase.table("users").select("*").eq("email", email).execute()
        users = res.data or []

        if not users:
            return jsonify({"message": "User not found"}), 401

        user = users[0]
        stored_hash = user.get("password_hash")
        if not stored_hash:
            return jsonify({"message": "No password found for user"}), 500

        # Verify password
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            session["user_id"] = user.get("user_id")
            session["user_name"] = user.get("full_name")
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": user.get("user_id"),
                    "name": user.get("full_name"),
                    "email": user.get("email")
                }
            }), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    except Exception as e:
        # Catch any Supabase errors
        return jsonify({"message": str(e)}), 500


# ------------------ LOGOUT ------------------
@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200
