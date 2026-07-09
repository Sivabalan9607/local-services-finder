from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SECRET_KEY in environment variables.")

# Create Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Upload directory helper
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

def get_db():
    """
    Dependency helper that returns the Supabase client instance.
    """
    return supabase

def init_db():
    """
    No-op stub for Supabase (as tables are created in Supabase SQL editor).
    We just ensure the uploads folder is created locally.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    print("Local uploads folder verified. Please ensure supabase_schema.sql is executed in your Supabase Dashboard.")
