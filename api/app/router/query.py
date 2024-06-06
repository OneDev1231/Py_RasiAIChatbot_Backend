from typing import List
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
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

QUERY_API_URL = "https://sales-ai-chatbot-llm.onrender.com/api/v1/prediction/4274ec33-3677-44c7-916f-7f6224869c61"

extension_list = ["csv", "docx", "pdf", "json"]

class AddChatbotRequest(BaseModel):
    chatbotName: str

@router.post("/add_chatbot")
async def add_chatbot(request: AddChatbotRequest, current_user: dict = Depends(get_current_user)):
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
    current_user: dict = Depends(get_current_user)
):
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
        async with httpx.AsyncClient() as client:
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
    