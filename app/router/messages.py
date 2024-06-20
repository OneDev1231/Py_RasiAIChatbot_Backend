from datetime import datetime
from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from supabase import create_client, Client

from ..utils.llm_query import llm_query

from ..utils.embed import embed_file, embed_text
from ..utils.get_user import get_current_user
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_ANON_PUBLIC_KEY = os.getenv("SUPABASE_ANON_PUBLIC_KEY")
LLM_BEARER_TOKEN = os.getenv("LLM_BEARER_TOKEN")
supabase: Client = create_client(SUPABASE_PROJECT_URL, SUPABASE_ANON_PUBLIC_KEY)


router = APIRouter()

@router.post("/get_test_msgGroup")
async def get_test_msg(
    request: Request,
    response: Response,
    chatbotname: str = Form(...),
    user_data: Tuple[dict, Optional[str], Optional[str]] = Depends(get_current_user)
):
    print(chatbotname)
    current_user, updated_access_token, updated_refresh_token = user_data

    request.state.updated_access_token = updated_access_token
    request.state.updated_refresh_token = updated_refresh_token

    user_id = current_user.user.id
    response = supabase.table("test_chat_history").select("*").eq('chatbotName', chatbotname).eq('user_id', user_id).execute()
    print(response)
    final_response = {}
    if not response.data:
        final_response = {'messages': []}
    final_response = JSONResponse(content={'messages': response.data})

    if updated_access_token and updated_refresh_token:
        is_production = os.getenv("ENV") == "production"
        print(is_production)
        if is_production:
            final_response.set_cookie(
                key="access_token",
                value=updated_access_token,
                httponly=False,
                secure=True,
                samesite="Lax",
                domain='.rasi.ai',
            )
            final_response.set_cookie(
                key="refresh_token",
                value=updated_refresh_token,
                httponly=False,
                secure=True,
                samesite="Lax",
                domain='.rasi.ai',
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

@router.post("/send_message")
async def send_message(
    request: Request,
    response: Response,
    botcheck: bool = Form(...),
    message: str = Form(...),
    createdAt: str = Form(...),
    chatbotName: str = Form(...),
    user_data: Tuple[dict, Optional[str], Optional[str]] = Depends(get_current_user)
):
    current_user, updated_access_token, updated_refresh_token = user_data

    request.state.updated_access_token = updated_access_token
    request.state.updated_refresh_token = updated_refresh_token

    user_id = current_user.user.id

    #--- Get User Email
    user_response = supabase.table("business_owner").select("email").eq('id', user_id).execute()

    if not user_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_email = user_response.data[0]['email']
    #-----Insert user message onto the message history table.
    try:
        insert_response = supabase.table("test_chat_history").insert(
            {
                "chatbotName": chatbotName,
                "user_id": user_id,
                "message": message,
                "botcheck": botcheck,
                "created_at": createdAt,
            }
        ).execute()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=501, detail=str(e))

    if not insert_response.data:
        raise HTTPException(status_code=500, detail="Failed to insert data")
    
    #-----Get the prompt of the chatbot
    prompt_response = supabase.table("chatbot").select("prompt").eq('chatbotName', chatbotName).eq('user_id', user_id).execute()
    print(prompt_response)

    if not prompt_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    
    prompt = prompt_response.data[0]['prompt']
    llm_response = await llm_query(email=user_email, message=message, chatbotName=chatbotName, prompt=prompt)
    print(llm_response)
    reply_message = llm_response['text']
    current_time = datetime.now().isoformat()
    try:
        insert_response = supabase.table("test_chat_history").insert(
            {
                "chatbotName": chatbotName,
                "user_id": user_id,
                "message": reply_message,
                "botcheck": True,
                "created_at": current_time,
            }
        ).execute()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=501, detail=str(e))
    

    final_response = JSONResponse(content={
        'message': reply_message,
        'createdAt': current_time,
    })
    if updated_access_token and updated_refresh_token:
        is_production = os.getenv("ENV") == "production"
        print(is_production)
        if is_production:
            final_response.set_cookie(
                key="access_token",
                value=updated_access_token,
                httponly=False,
                secure=True,
                samesite="Lax",
                domain='.rasi.ai',
            )
            final_response.set_cookie(
                key="refresh_token",
                value=updated_refresh_token,
                httponly=False,
                secure=True,
                samesite="Lax",
                domain='.rasi.ai',
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