from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from ..utils.get_user import get_current_user
from dotenv import load_dotenv
import httpx

import os
load_dotenv()

# Initialize Supabase client
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_ANON_PUBLIC_KEY = os.getenv("SUPABASE_ANON_PUBLIC_KEY")
LLM_BEARER_TOKEN = os.getenv("LLM_BEARER_TOKEN")
supabase: Client = create_client(SUPABASE_PROJECT_URL, SUPABASE_ANON_PUBLIC_KEY)


router = APIRouter()

@router.post("/getChatbots")
async def getChatbots(
    user_data: Tuple[dict, Optional[str], Optional[str]] = Depends(get_current_user)
):
    current_user, updated_access_token, updated_refresh_token = user_data
    user_id = current_user.user.id
    response = supabase.table("chatbot").select("*").eq('user_id', user_id).execute()
    print(response.data)
    final_response = JSONResponse(content=response.data)
    if updated_access_token and updated_refresh_token:
        is_production = os.getenv("ENV") == "production"
        print(is_production)
        if is_production:
            final_response.set_cookie(
                key="access_token",
                value=updated_access_token,
                httponly=False,
                secure=True,
                samesite="None",
            )
            final_response.set_cookie(
                key="refresh_token",
                value=updated_refresh_token,
                httponly=False,
                secure=True,
                samesite="None",
            )
        else:
            final_response.set_cookie(
                key="access_token",
                value=updated_access_token,
                httponly=False,
                secure=False,
                samesite="Lax",
            )
            final_response.set_cookie(
                key="refresh_token",
                value=updated_refresh_token,
                httponly=False,
                secure=False,
                samesite="Lax",
            )
    return final_response