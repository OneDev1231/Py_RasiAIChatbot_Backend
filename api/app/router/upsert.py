from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
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

LLM_API_URL = {
    "csv": 'https://sales-ai-chatbot-llm.onrender.com/api/v1/vector/upsert/07674a31-a5bb-42c7-ac4b-652fa54f62e4',
    "docx": 'https://sales-ai-chatbot-llm.onrender.com/api/v1/vector/upsert/6c057a26-0cd7-480e-b3d6-8a27cfdd2376',
    "pdf": 'https://sales-ai-chatbot-llm.onrender.com/api/v1/vector/upsert/a9dce05f-2f47-4b25-b18e-57b65b423ca0',
    "json": 'https://sales-ai-chatbot-llm.onrender.com/api/v1/vector/upsert/3e7d998e-f502-4c64-95ec-2de99b4b086d'
}

extension_list = ["csv", "docx", "pdf", "json"]

class AddChatbotRequest(BaseModel):
    chatbotName: str
    prompt: str
             


@router.post("/add_chatbot")
async def add_chatbot(request: AddChatbotRequest, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    print(current_user)
    print(type(current_user))
    user_id = current_user.user.id
    record_data = {
        "chatbotName": request.chatbotName,
        "user_id": user_id
    }
    try:
        response = supabase.table("chatbot").insert(record_data).execute()
        print("Row added:", response.data)
    except Exception as e:
        print("error: ", e)

@router.post("/upsert_file/")
async def upsert_file(
    file: UploadFile = File(...),
    chatbotName: str = Form(...),
    user_data: Tuple[dict, Optional[str], Optional[str]] = Depends(get_current_user)
):
    current_user, updated_access_token, updated_refresh_token = user_data
    user_id = current_user.user.id
    response = supabase.table("business_owner").select("email").eq('id', user_id).execute()
    user_email = response.data[0]['email']

    file_contents =  await file.read()
    file_extension = file.filename.split('.')[-1].lower()
    file_to_send = ("files", (file.filename, file_contents, file.content_type))
    file_name = file.filename

    # print(files_name)
    headers = {
        "Authorization": f"Bearer {LLM_BEARER_TOKEN}"
    }

    data = {
        "pineconeNamespace": f"{user_email}-{chatbotName}",
        "tableName": f"{user_email}-{chatbotName}",
        "namespace": f"{user_email}-{chatbotName}",
        "metadata": f'{{"source": "{file_name}"}}'
    }
    print(data)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=30.0)) as client:
            response = await client.post(
                LLM_API_URL[file_extension],
                headers=headers,
                data=data,
                files=[file_to_send]
            )
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request timed out while contacting the third-party API"
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while requesting {exc.request.url}: {str(exc)}"
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.text
        )
    final_response = JSONResponse(content={
        'status': 'success',
        'data': 'File uploaded successfully',
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