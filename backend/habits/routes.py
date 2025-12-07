from flask import Blueprint, request, jsonify, session
import sys
import os

# Path fix to find db.py in parent folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_supabase_client

habits_bp = Blueprint("habits", __name__)

# --------------------------------------------------------
#                 GET ALL HABITS
# --------------------------------------------------------
@habits_bp.get("/")
def get_habits():
    """Get all habits for the current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        response = supabase.table('habits').select('*').eq('user_id', user_id).execute()
        return jsonify({"habits": response.data}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --------------------------------------------------------
#                 CREATE HABIT
# --------------------------------------------------------
@habits_bp.post("/")
def create_habit():
    """Create a new habit"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    data = request.json
    habit_name = data.get("habit_name")
    frequency = data.get("frequency", "daily")  # daily or weekly
    
    if not habit_name:
        return jsonify({"message": "Habit name is required"}), 400
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        response = supabase.table('habits').insert({
            'user_id': user_id,
            'habit_name': habit_name,
            'frequency': frequency,
            'plant_state': 'flourishing'
        }).execute()
        return jsonify({"message": "Habit created successfully", "habit": response.data[0] if response.data else None}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --------------------------------------------------------
#                 UPDATE HABIT (Water/Complete)
# --------------------------------------------------------
@habits_bp.put("/<string:habit_id>")
def update_habit(habit_id):
    """Update a habit (e.g., mark as watered/completed)"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        # Update last_watered timestamp and set plant_state to flourishing
        from datetime import datetime
        response = supabase.table('habits').update({
            'last_watered': datetime.utcnow().isoformat(),
            'plant_state': 'flourishing'
        }).eq('habit_id', habit_id).eq('user_id', user_id).execute()
        
        if not response.data:
            return jsonify({"message": "Habit not found"}), 404
        
        return jsonify({"message": "Habit updated successfully", "habit": response.data[0]}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --------------------------------------------------------
#                 DELETE HABIT
# --------------------------------------------------------
@habits_bp.delete("/<string:habit_id>")
def delete_habit(habit_id):
    """Delete a habit"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        response = supabase.table('habits').delete().eq('habit_id', habit_id).eq('user_id', user_id).execute()
        if not response.data:
            return jsonify({"message": "Habit not found"}), 404
        return jsonify({"message": "Habit deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

