from fastapi import Cookie, HTTPException
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv

import os
load_dotenv()

# Initialize Supabase client
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_ANON_PUBLIC_KEY = os.getenv("SUPABASE_ANON_PUBLIC_KEY")
supabase: Client = create_client(SUPABASE_PROJECT_URL, SUPABASE_ANON_PUBLIC_KEY)

def get_current_user(access_token: Optional[str] = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing")
    user = supabase.auth.get_user(access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user