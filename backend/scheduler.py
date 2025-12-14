import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from db import get_supabase_client
# from email_service import send_wilting_reminder_email  # Commented out - visible for review
from reminder_storage import add_reminder
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
        
        # Format thresholds for database comparison (ensure ISO format without microseconds)
        daily_threshold_str = daily_threshold.strftime('%Y-%m-%dT%H:%M:%S')
        weekly_threshold_str = weekly_threshold.strftime('%Y-%m-%dT%H:%M:%S')
        
        logger.info(f"Checking for wilting plants. Daily threshold: {daily_threshold_str}, Weekly threshold: {weekly_threshold_str}")
        
        # Update Daily Habits (20 hours threshold)
        # Update all habits (except already wilting ones) where last_watered is more than 20 hours ago
        daily_response = (supabase.table('habits')
                         .update({'plant_state': 'wilting'})
                         .eq('frequency', 'daily')
                         .lt('last_watered', daily_threshold_str)
                         .neq('plant_state', 'wilting')
                         .execute())
        daily_updated = len(daily_response.data) if daily_response.data else 0

        # Update Weekly Habits (140 hours threshold)
        weekly_response = (supabase.table('habits')
                          .update({'plant_state': 'wilting'})
                          .eq('frequency', 'weekly')
                          .lt('last_watered', weekly_threshold_str)
                          .neq('plant_state', 'wilting')
                          .execute())
        weekly_updated = len(weekly_response.data) if weekly_response.data else 0

        logger.info(f"Updated Plants: {daily_updated} daily became wilting, {weekly_updated} weekly became wilting.")
        
        # Debug: Log some habits to see what's happening
        if daily_updated == 0 and weekly_updated == 0:
            # Check what habits exist
            all_habits = supabase.table('habits').select('habit_id, habit_name, frequency, plant_state, last_watered').limit(5).execute()
            if all_habits.data:
                logger.info(f"Debug: Found {len(all_habits.data)} habits (showing first 5)")
                for h in all_habits.data:
                    logger.info(f"  - {h.get('habit_name')}: state={h.get('plant_state')}, last_watered={h.get('last_watered')}, freq={h.get('frequency')}")
            
    except Exception as e:
        logger.error(f"Error updating plant states: {e}")
        import traceback
        logger.error(traceback.format_exc())

def send_reminder_emails():
    """
    Finds users with 'wilting' plants and sends them an email reminder using Resend.
    Sends emails to the user's signup email address.
    """
    supabase = get_supabase_client()
    if not supabase:
        logger.error("Could not connect to DB for email reminders.")
        return

    try:
        # Query wilting habits with user info
        habits_response = supabase.table('habits').select('user_id, habit_name').eq('plant_state', 'wilting').execute()
        
        if not habits_response.data:
            logger.info("No wilting plants found, skipping email reminders.")
            return
        
        # Get unique user IDs
        user_ids = list(set([h['user_id'] for h in habits_response.data]))
        
        # Get user emails - Query users for each user_id
        users_dict = {}
        for uid in user_ids:
            try:
                user_response = supabase.table('users').select('user_id, email, full_name').eq('user_id', uid).execute()
                if user_response.data and len(user_response.data) > 0:
                    users_dict[uid] = user_response.data[0]
            except Exception as e:
                logger.error(f"Error fetching user {uid}: {e}")
        
        if not users_dict:
            logger.warning("No users found for wilting habits.")
            return
        
        # Create a mapping of user_id to habits
        habits_by_user = {}
        for h in habits_response.data:
            user_id = h['user_id']
            if user_id not in habits_by_user:
                habits_by_user[user_id] = []
            habits_by_user[user_id].append(h['habit_name'])
        
        # Store reminders for display on website (like OTP popup)
        # Also attempt to send via Resend API (may fail due to free tier restrictions)
        for user_id, user_info in users_dict.items():
            if user_id in habits_by_user:
                habit_names = habits_by_user[user_id]
                
                # Store reminder for website popup display
                add_reminder(user_id, habit_names)
                logger.info(f"Reminder stored for user {user_id} ({user_info['email']}) for {len(habit_names)} habit(s)")
                
                # ====================================================================
                # RESEND EMAIL API CALL - COMMENTED OUT (Visible for review)
                # ====================================================================
                # Free tier email services don't allow scheduled emails without domain purchase
                # This code is kept for reference and can be uncommented once a domain is purchased
                # 
                # try:
                #     result = send_wilting_reminder_email(
                #         user_email=user_info['email'],
                #         user_name=user_info['full_name'],
                #         habit_names=habit_names
                #     )
                #     if result:
                #         logger.info(f"Wilting reminder email also sent to {user_info['email']} for {len(habit_names)} habit(s)")
                #     else:
                #         logger.info(f"Email sending failed for {user_info['email']} (expected in free tier - reminder will show on website)")
                # except Exception as mail_err:
                #     logger.info(f"Email sending exception for {user_info['email']}: {mail_err} (expected in free tier - reminder will show on website)")
                # ====================================================================

    except Exception as e:
        logger.error(f"Error sending reminders: {e}")
        import traceback
        logger.error(traceback.format_exc())

def start_scheduler():
    """
    Starts the background scheduler for plant state updates and email reminders.
    No longer requires app or mail parameters since we use Resend directly.
    """
    scheduler = BackgroundScheduler()
    
    # 1. Task: Update Plant States (Run every hour)
    scheduler.add_job(func=update_plant_states, trigger="interval", hours=1)
    
    # 2. Task: Send Email Reminders (Run daily)
    # Using 'interval' hours for testing purposes, change to 'cron' for production
    # Example for daily at 9:00 AM: trigger="cron", hour=9, minute=0
    scheduler.add_job(func=send_reminder_emails, trigger="interval", hours=24)

    scheduler.start()
    logger.info("Scheduler started: Plant state updates (hourly) and email reminders (daily)")
    
    # Shut down scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

