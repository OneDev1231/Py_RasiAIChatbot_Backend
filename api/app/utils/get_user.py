from fastapi import Cookie, HTTPException
from httpx import AsyncClient
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv
import time

import os
load_dotenv()

# Initialize Supabase client
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_ANON_PUBLIC_KEY = os.getenv("SUPABASE_ANON_PUBLIC_KEY")
supabase: Client = create_client(SUPABASE_PROJECT_URL, SUPABASE_ANON_PUBLIC_KEY)


def get_refresh_token(refresh_token: str):
    response = supabase.auth.refresh_session(refresh_token).model_dump()
    # print(response)
    if response.get("error"):
        raise HTTPException(status_code=401, detail=response["error"]["message"])
    return response['session']['access_token'], response['session']['refresh_token']


def is_token_expired(token: str) -> bool:
    payload = supabase.auth._decode_jwt(token)
    print(payload['exp'])
    print(time.time())
    if payload['exp'] > time.time():
        print("Access Token is still valid")
        return False
    else:
        print("Access token is expired")
        return True

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