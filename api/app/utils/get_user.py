from datetime import datetime, time, timezone
from fastapi import Cookie, HTTPException
from httpx import AsyncClient
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv

import os
load_dotenv()

# Initialize Supabase client
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_ANON_PUBLIC_KEY = os.getenv("SUPABASE_ANON_PUBLIC_KEY")
supabase: Client = create_client(SUPABASE_PROJECT_URL, SUPABASE_ANON_PUBLIC_KEY)


def get_refresh_token(refresh_token: str):
    response = supabase.auth._refresh_access_token(refresh_token=refresh_token).model_dump()
    print(response)
    if response.get("error"):
        raise HTTPException(status_code=401, detail=response["error"]["message"])
    return response.get("access_token"), response.get("refresh_token")


def is_token_expired(token: str) -> bool:
    user = supabase.auth.get_session()
    print(user)
    current_time = datetime.now()
    if user and user.expires_at < current_time:
        print("Access token has expired!")
    else:
        print("Access token is still valid")

def get_current_user(access_token: Optional[str] = Cookie(None), refresh_token: Optional[str] = Cookie(None)):
    print(access_token)
    print(refresh_token)
    if not access_token or not refresh_token:
        raise HTTPException(status_code=401, detail="Access token missing")

    updated_access_token = None
    updated_refresh_token = None

    if is_token_expired(access_token):
        print("Here")
        access_token, refresh_token = get_refresh_token(refresh_token)
        updated_access_token = access_token
        updated_refresh_token = refresh_token
    print(access_token)
    print(refresh_token)
    user = supabase.auth.get_user(access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user, updated_access_token, updated_refresh_token