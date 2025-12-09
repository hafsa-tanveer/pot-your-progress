"""
Habits Routes - Backend API for Habit Tracking

This module implements the habit tracking system where users can:
- Create, read, update, and delete habits
- Track habit completions by clicking water droplets (POST /habits/<habit_id>/complete)
- Mark habits as completed for the day (daily habits) or week (weekly habits)
- Automatically revive wilting plants when a habit is completed
- Prevent duplicate completions for the same period (day/week)
- View completion history and statistics

Key Features:
- Water Droplet Tracking: POST /habits/<habit_id>/complete marks a habit as completed
- Plant Revival: Wilting plants are automatically set to 'flourishing' when completed
- Duplicate Prevention: Prevents marking the same habit as completed multiple times in the same period
- Completion History: GET /habits/<habit_id>/completions returns completion history
"""

from flask import Blueprint, request, jsonify, session
import sys
import os
from datetime import datetime, timedelta, date

# Path fix to find db.py in parent folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_supabase_client

habits_bp = Blueprint("habits", __name__)

# Helper function to get the period key for tracking completions
def get_period_key(frequency, completion_date=None):
    """
    Returns a unique key for the completion period.
    For daily: returns the date string (YYYY-MM-DD)
    For weekly: returns the year and week number (YYYY-WW)
    """
    if completion_date is None:
        completion_date = date.today()
    
    if frequency == "daily":
        return completion_date.isoformat()  # Returns YYYY-MM-DD
    elif frequency == "weekly":
        # Get ISO week number
        year, week, _ = completion_date.isocalendar()
        return f"{year}-W{week:02d}"
    return None

def get_week_start_end(completion_date):
    """Get the start and end dates of the week for a given date"""
    year, week, weekday = completion_date.isocalendar()
    # Calculate start of week (Monday)
    days_since_monday = weekday - 1
    start_of_week = completion_date - timedelta(days=days_since_monday)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def parse_datetime_safe(dt_string):
    """Safely parse datetime string, handling various formats"""
    if not dt_string:
        return None
    try:
        # Remove timezone info for comparison
        dt_string = dt_string.replace('Z', '').replace('+00:00', '')
        if '.' in dt_string:
            dt_string = dt_string.split('.')[0]  # Remove microseconds
        return datetime.fromisoformat(dt_string)
    except:
        try:
            # Try parsing with different format
            return datetime.strptime(dt_string.split('T')[0], '%Y-%m-%d')
        except:
            return None

def is_already_completed(supabase, habit_id, frequency, completion_date=None):
    """
    Check if the habit is already completed for the current period (day/week).
    Returns True if already completed, False otherwise.
    """
    if completion_date is None:
        completion_date = date.today()
    
    period_key = get_period_key(frequency, completion_date)
    if not period_key:
        return False
    
    try:
        # Check if there's a completion record for this habit and period
        if frequency == "daily":
            # Check if there's a completion today
            start_of_day = datetime.combine(completion_date, datetime.min.time())
            end_of_day = datetime.combine(completion_date, datetime.max.time())
            
            # Query habit_completions table if it exists
            try:
                response = supabase.table('habit_completions').select('*').eq('habit_id', habit_id).eq('period_key', period_key).execute()
                if response.data and len(response.data) > 0:
                    return True
            except:
                pass
            
            # Fallback: check last_watered in habits table
            try:
                habit_response = supabase.table('habits').select('last_watered').eq('habit_id', habit_id).execute()
                if habit_response.data and habit_response.data[0].get('last_watered'):
                    last_watered = parse_datetime_safe(habit_response.data[0]['last_watered'])
                    if last_watered and start_of_day.date() <= last_watered.date() <= end_of_day.date():
                        return True
            except:
                pass
                
        elif frequency == "weekly":
            # Get the start and end of the week
            start_of_week, end_of_week = get_week_start_end(completion_date)
            
            # Query habit_completions table if it exists
            try:
                response = supabase.table('habit_completions').select('*').eq('habit_id', habit_id).eq('period_key', period_key).execute()
                if response.data and len(response.data) > 0:
                    return True
            except:
                pass
            
            # Fallback: check last_watered
            try:
                habit_response = supabase.table('habits').select('last_watered').eq('habit_id', habit_id).execute()
                if habit_response.data and habit_response.data[0].get('last_watered'):
                    last_watered = parse_datetime_safe(habit_response.data[0]['last_watered'])
                    if last_watered and start_of_week <= last_watered.date() <= end_of_week:
                        return True
            except:
                pass
    except Exception as e:
        # If there's an error, assume not completed to allow the action
        print(f"Error checking completion status: {e}")
        return False
    
    return False

# --------------------------------------------------------
#                 GET ALL HABITS
# --------------------------------------------------------
@habits_bp.get("/")
def get_habits():
    """Get all habits for the current user with completion status"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        response = supabase.table('habits').select('*').eq('user_id', user_id).execute()
        habits = response.data if response.data else []
        
        # Add completion status for each habit
        for habit in habits:
            habit_id = habit.get('habit_id')
            frequency = habit.get('frequency', 'daily')
            is_completed = is_already_completed(supabase, habit_id, frequency)
            
            if frequency == 'daily':
                habit['is_completed_today'] = is_completed
            else:
                habit['is_completed_this_week'] = is_completed
        
        return jsonify({"habits": habits}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --------------------------------------------------------
#                 CREATE HABIT
# --------------------------------------------------------
@habits_bp.post("")
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
            'plant_state': 'flourishing',
            'last_watered': None
        }).execute()
        return jsonify({"message": "Habit created successfully", "habit": response.data[0] if response.data else None}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --------------------------------------------------------
#                 TRACK COMPLETION (Water Droplet Click)
# --------------------------------------------------------
@habits_bp.post("/<string:habit_id>/complete")
def track_completion(habit_id):
    """
    Track a habit completion (water droplet click).
    - Marks the habit as completed for the current day/week
    - Revives wilting plants (sets to flourishing)
    - Prevents duplicate completions for the same period
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        # First, get the habit to check ownership and frequency
        habit_response = supabase.table('habits').select('*').eq('habit_id', habit_id).eq('user_id', user_id).execute()
        
        if not habit_response.data or len(habit_response.data) == 0:
            return jsonify({"message": "Habit not found"}), 404
        
        habit = habit_response.data[0]
        frequency = habit.get('frequency', 'daily')
        current_state = habit.get('plant_state', 'flourishing')
        
        # Check if already completed for this period
        if is_already_completed(supabase, habit_id, frequency):
            return jsonify({
                "message": "Habit already completed for this period",
                "habit": habit,
                "already_completed": True
            }), 200
        
        # Get current timestamp
        now = datetime.utcnow()
        completion_date = now.date()
        period_key = get_period_key(frequency, completion_date)
        
        # Create completion record (if habit_completions table exists)
        try:
            supabase.table('habit_completions').insert({
                'habit_id': habit_id,
                'user_id': user_id,
                'completion_date': completion_date.isoformat(),
                'completed_at': now.isoformat(),
                'period_key': period_key
            }).execute()
        except Exception as e:
            # If table doesn't exist, that's okay - we'll just update the habit
            print(f"Note: habit_completions table may not exist: {e}")
        
        # Update the habit: set last_watered and revive if wilting
        update_data = {
            'last_watered': now.isoformat()
        }
        
        # If plant is wilting, revive it to flourishing
        if current_state == 'wilting':
            update_data['plant_state'] = 'flourishing'
        
        # Update the habit
        update_response = supabase.table('habits').update(update_data).eq('habit_id', habit_id).eq('user_id', user_id).execute()
        
        if not update_response.data:
            return jsonify({"message": "Failed to update habit"}), 500
        
        updated_habit = update_response.data[0]
        was_revived = current_state == 'wilting'

        if frequency == 'daily':
            updated_habit['is_completed_today'] = True
            updated_habit['is_completed_this_week'] = False
        else:
            updated_habit['is_completed_today'] = False
            updated_habit['is_completed_this_week'] = True
        
        return jsonify({
            "message": "Habit completed successfully",
            "habit": updated_habit,
            "revived": was_revived,
            "already_completed": False,
            "completion_date": completion_date.isoformat(),
            "period_key": period_key
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error tracking completion: {str(e)}"}), 500

# --------------------------------------------------------
#                 UPDATE HABIT (General Update)
# --------------------------------------------------------
@habits_bp.put("/<string:habit_id>")
def update_habit(habit_id):
    """Update a habit (general update, e.g., edit habit name)"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        data = request.json
        update_data = {}
        
        # Allow updating habit_name if provided
        if 'habit_name' in data:
            update_data['habit_name'] = data['habit_name']
        
        # Allow updating frequency if provided
        if 'frequency' in data:
            if data['frequency'] not in ['daily', 'weekly']:
                return jsonify({"message": "Frequency must be 'daily' or 'weekly'"}), 400
            update_data['frequency'] = data['frequency']
        
        if not update_data:
            return jsonify({"message": "No valid fields to update"}), 400
        
        response = supabase.table('habits').update(update_data).eq('habit_id', habit_id).eq('user_id', user_id).execute()
        
        if not response.data:
            return jsonify({"message": "Habit not found"}), 404
        
        return jsonify({"message": "Habit updated successfully", "habit": response.data[0]}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --------------------------------------------------------
#                 GET SINGLE HABIT WITH COMPLETION STATUS
# --------------------------------------------------------
@habits_bp.get("/<string:habit_id>")
def get_habit(habit_id):
    """Get a single habit with its current completion status"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        response = supabase.table('habits').select('*').eq('habit_id', habit_id).eq('user_id', user_id).execute()
        
        if not response.data or len(response.data) == 0:
            return jsonify({"message": "Habit not found"}), 404
        
        habit = response.data[0]
        frequency = habit.get('frequency', 'daily')
        
        # Check if already completed for current period
        is_completed = is_already_completed(supabase, habit_id, frequency)
        
        habit['is_completed_today'] = is_completed if frequency == 'daily' else False
        habit['is_completed_this_week'] = is_completed if frequency == 'weekly' else False
        
        return jsonify({"habit": habit}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --------------------------------------------------------
#                 GET COMPLETION HISTORY
# --------------------------------------------------------
@habits_bp.get("/<string:habit_id>/completions")
def get_completion_history(habit_id):
    """Get completion history for a habit"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({"message": "Database connection failed"}), 500
    
    try:
        # Verify habit belongs to user
        habit_response = supabase.table('habits').select('frequency').eq('habit_id', habit_id).eq('user_id', user_id).execute()
        if not habit_response.data:
            return jsonify({"message": "Habit not found"}), 404
        
        frequency = habit_response.data[0].get('frequency', 'daily')
        
        # Get query parameters for date range
        days_back = request.args.get('days', type=int, default=30)
        start_date = date.today() - timedelta(days=days_back)
        
        # Try to get completions from habit_completions table
        try:
            response = supabase.table('habit_completions').select('*').eq('habit_id', habit_id).gte('completion_date', start_date.isoformat()).order('completed_at', desc=True).execute()
            completions = response.data if response.data else []
        except:
            # If table doesn't exist, return empty list
            completions = []
        
        # Also check last_watered from habits table as fallback
        habit_full = supabase.table('habits').select('last_watered').eq('habit_id', habit_id).execute()
        if habit_full.data and habit_full.data[0].get('last_watered'):
            last_watered_str = habit_full.data[0]['last_watered']
            try:
                last_watered = datetime.fromisoformat(last_watered_str.replace('Z', '+00:00'))
                if last_watered.date() >= start_date:
                    # Add to completions if not already there
                    found = False
                    for comp in completions:
                        if comp.get('completion_date') == last_watered.date().isoformat():
                            found = True
                            break
                    if not found:
                        completions.append({
                            'completion_date': last_watered.date().isoformat(),
                            'completed_at': last_watered.isoformat(),
                            'period_key': get_period_key(frequency, last_watered.date())
                        })
            except:
                pass
        
        return jsonify({
            "habit_id": habit_id,
            "frequency": frequency,
            "completions": completions,
            "total_completions": len(completions)
        }), 200
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

