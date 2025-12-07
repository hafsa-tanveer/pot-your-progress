import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message
from db import get_supabase_client
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HabitScheduler")

def update_plant_states():
    """
    Checks all flourishing plants. 
    - Daily habits wilt after 20 hours.
    - Weekly habits wilt after 140 hours.
    Updates the database state to 'wilting'.
    """
    supabase = get_supabase_client()
    if not supabase:
        logger.error("Could not connect to DB for scheduled task.")
        return

    try:
        from datetime import datetime, timedelta
        
        # Calculate thresholds
        daily_threshold = datetime.utcnow() - timedelta(hours=20)
        weekly_threshold = datetime.utcnow() - timedelta(hours=140)
        
        # Update Daily Habits (20 hours threshold)
        daily_response = supabase.table('habits').update({
            'plant_state': 'wilting'
        }).eq('frequency', 'daily').eq('plant_state', 'flourishing').lt('last_watered', daily_threshold.isoformat()).execute()
        daily_updated = len(daily_response.data) if daily_response.data else 0

        # Update Weekly Habits (140 hours threshold)
        weekly_response = supabase.table('habits').update({
            'plant_state': 'wilting'
        }).eq('frequency', 'weekly').eq('plant_state', 'flourishing').lt('last_watered', weekly_threshold.isoformat()).execute()
        weekly_updated = len(weekly_response.data) if weekly_response.data else 0

        if daily_updated > 0 or weekly_updated > 0:
            logger.info(f"Updated Plants: {daily_updated} daily became wilting, {weekly_updated} weekly became wilting.")
            
    except Exception as e:
        logger.error(f"Error updating plant states: {e}")

def send_reminder_emails(app, mail):
    """
    Finds users with 'wilting' plants and sends them an email reminder.
    """
    with app.app_context():
        supabase = get_supabase_client()
        if not supabase:
            return

        try:
            # Join Users and Habits to get email addresses for wilting plants
            # Using Supabase to query wilting habits with user info
            habits_response = supabase.table('habits').select('user_id, habit_name').eq('plant_state', 'wilting').execute()
            
            if not habits_response.data:
                return
            
            # Get unique user IDs
            user_ids = list(set([h['user_id'] for h in habits_response.data]))
            
            # Get user emails - Query users for each user_id
            # Note: Supabase Python client may need individual queries or use a different filter method
            users_dict = {}
            for uid in user_ids:
                try:
                    user_response = supabase.table('users').select('user_id, email, full_name').eq('user_id', uid).execute()
                    if user_response.data and len(user_response.data) > 0:
                        users_dict[uid] = user_response.data[0]
                except Exception as e:
                    logger.error(f"Error fetching user {uid}: {e}")
            
            if not users_dict:
                return
            
            # Create a mapping of user_id to habits
            habits_by_user = {}
            for h in habits_response.data:
                user_id = h['user_id']
                if user_id not in habits_by_user:
                    habits_by_user[user_id] = []
                habits_by_user[user_id].append(h['habit_name'])
            
            # Send emails
            for user_id, user_info in users_dict.items():
                if user_id in habits_by_user:
                    habit_names = habits_by_user[user_id]
                    for habit_name in habit_names:
                        try:
                            msg = Message(
                                subject="Your Habit Garden Needs You!",
                                sender=app.config.get("MAIL_USERNAME"),
                                recipients=[user_info['email']]
                            )
                            msg.body = f"Hi {user_info['full_name']},\n\nYour plant for '{habit_name}' is wilting! Log in to Pot Your Progress and track your habit to save it.\n\nKeep growing,\nTeam Flora"
                            mail.send(msg)
                            logger.info(f"Reminder sent to {user_info['email']} for {habit_name}")
                        except Exception as mail_err:
                            logger.error(f"Failed to send email to {user_info['email']}: {mail_err}")

        except Exception as e:
            logger.error(f"Error sending reminders: {e}")

def start_scheduler(app, mail):
    scheduler = BackgroundScheduler()
    
    # 1. Task: Update Plant States (Run every hour)
    scheduler.add_job(func=update_plant_states, trigger="interval", hours=1)
    
    # 2. Task: Send Email Reminders (Run daily at 9:00 AM or frequency of your choice)
    # Using 'interval' hours for testing purposes, change to 'cron' for production
    scheduler.add_job(func=lambda: send_reminder_emails(app, mail), trigger="interval", hours=24)

    scheduler.start()
    
    # Shut down scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

