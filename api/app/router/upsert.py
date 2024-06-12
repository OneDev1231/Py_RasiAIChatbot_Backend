from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile, HTTPException, status
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

@router.post("/upsert_file")
async def upsert_file(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    chatbotName: str = Form(...),
    user_data: Tuple[dict, Optional[str], Optional[str]] = Depends(get_current_user)
):
    current_user, updated_access_token, updated_refresh_token = user_data

    request.state.updated_access_token = updated_access_token
    request.state.updated_refresh_token = updated_refresh_token


    user_id = current_user.user.id
    response = supabase.table("business_owner").select("email").eq('id', user_id).execute()

    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_email = response.data[0]['email']

    file_contents =  await file.read()
    file_extension = file.filename.split('.')[-1].lower()
    file_to_send = ("files", (file.filename, file_contents, file.content_type))
    file_name = file.filename

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
            api_response = await client.post(
                LLM_API_URL[file_extension],
                headers=headers,
                data=data,
                files=[file_to_send]
            )
            print("API Response:", api_response)
            print("Response Status Code:", api_response.status_code)
            print("Response Content:", api_response.text)

        if api_response.status_code != 200:
            print("here")  # Adjust `200` if your API uses different success codes
            raise HTTPException(status_code=api_response.status_code, detail="Error Occurred")    
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))

    try:
        store_response = supabase.rpc(
            'update_upsert_file_list',
            {
                'chatbot_name': chatbotName,
                'new_file': file_name
            }
        ).execute()
        # return {"message": "File appended successfully"}
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))
    
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