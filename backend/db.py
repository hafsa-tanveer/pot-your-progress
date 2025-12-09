import os

from supabase import create_client, Client

# === CREDENTIALS ===
# Replace these with your actual Supabase URL and Key
SUPABASE_URL = "https://cajlndfhrmfyxvhxtgbp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNhamxuZGZocm1meXh2aHh0Z2JwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM5NTc4NTYsImV4cCI6MjA3OTUzMzg1Nn0.HOt5_TPHUoyieTipiruJYaLzfm06bn0nlfkZ0q53Ge8"

def get_supabase_client() -> Client:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        print(f"❌ Supabase Connection Error: {e}")
        return None