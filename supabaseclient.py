from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()
URL=os.getenv("SUPABASE_URL")
KEY=os.getenv("SUPABASE_KEY")

supabase=create_client(URL,KEY)

