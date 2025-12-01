from flask import Blueprint, request, jsonify, session
import sys
import os

# Import the dummy database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dummy_db as oracledb
from dummy_db import get_db_connection

habits_bp = Blueprint("habits", __name__)

def get_current_user_id():
    return 1 # Bypass auth for testing

# --- GET HABITS ---
@habits_bp.get("/")
def get_habits():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        ref_cursor = cursor.callfunc("get_user_habits", oracledb.CURSOR, [get_current_user_id()])
        habits = []
        for row in ref_cursor:
            habits.append({
                "id": row[0],
                "name": row[1], # Map 'habit_name' to 'name' for frontend
                "schedule": row[2],
                "state": row[3],
                "last_watered": row[4]
            })
        return jsonify(habits), 200
    finally:
        cursor.close()
        conn.close()

# --- ADD HABIT ---
@habits_bp.post("/add")
def add_habit():
    data = request.json
    # Frontend sends { name: "..." }, Backend expects habit_name
    habit_name = data.get("name") 
    schedule = data.get("schedule", "daily")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        plant_id_out = cursor.var(oracledb.NUMBER)
        cursor.callproc("create_habit", [get_current_user_id(), habit_name, schedule, plant_id_out])
        conn.commit()
        return jsonify({"message": "Added", "id": plant_id_out.getvalue()[0]}), 201
    finally:
        cursor.close()
        conn.close()

# --- EDIT/TRACK HABIT ---
@habits_bp.put("/<int:plant_id>")
def edit_habit(plant_id):
    data = request.json
    new_name = data.get("name")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # If just watering/tracking
        if not new_name:
            out_ts = cursor.var(oracledb.TIMESTAMP)
            cursor.callproc("track_habit", [plant_id, get_current_user_id(), out_ts])
        else:
            # If renaming (requires update_habit_details in dummy_db)
            cursor.callproc("update_habit_details", [plant_id, get_current_user_id(), new_name])
            
        conn.commit()
        return jsonify({"message": "Updated"}), 200
    finally:
        cursor.close()
        conn.close()

# --- DELETE HABIT ---
@habits_bp.delete("/<int:plant_id>")
def delete_habit(plant_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc("delete_habit", [plant_id, get_current_user_id()])
        conn.commit()
        return jsonify({"message": "Deleted"}), 200
    finally:
        cursor.close()
        conn.close()