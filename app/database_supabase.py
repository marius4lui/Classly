import os
from supabase import create_client, Client
from app.database import Base, SessionLocal
# Although this file is named database_supabase, we are setting up the Client here.
# NOTE: The rest of the app heavily relies on SQLAlchemy Sessions (SessionLocal).
# To make "Native Supabase" work, we would essentially be rewriting the Provider layer.

# However, for a "hybrid" approach where we use Native Supabase for specific features
# while keeping the core running, we can expose the client here.

# Ideally, we should check if SUPABASE_URL is set.
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

class SupabaseManager:
    _instance = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            if not SUPABASE_URL or not SUPABASE_KEY:
                # Fallback or Error? For now returning None or raising
                raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set for native Supabase support.")
            cls._instance = create_client(SUPABASE_URL, SUPABASE_KEY)
        return cls._instance

def get_supabase():
    try:
        return SupabaseManager.get_client()
    except Exception as e:
        print(f"Supabase Client Error: {e}")
        return None
