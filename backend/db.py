import os

from supabase import create_client, Client

# === CREDENTIALS ===
# Replace these with your actual Supabase URL and Key
SUPABASE_URL = "YOUR_SUPABASE_PROJECT_URL"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"

def get_supabase_client() -> Client:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        print(f"❌ Supabase Connection Error: {e}")
        return None