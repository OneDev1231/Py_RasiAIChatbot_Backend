
from fastapi import File, HTTPException
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client
from ..utils.get_user import get_current_user
from dotenv import load_dotenv
import httpx

import os
load_dotenv()

LLM_BEARER_TOKEN = os.getenv("LLM_BEARER_TOKEN")
LLM_API_URL = {
    "csv": 'https://sales-ai-chatbot-llm.onrender.com/api/v1/vector/upsert/07674a31-a5bb-42c7-ac4b-652fa54f62e4',
    "docx": 'https://sales-ai-chatbot-llm.onrender.com/api/v1/vector/upsert/6c057a26-0cd7-480e-b3d6-8a27cfdd2376',
    "pdf": 'https://sales-ai-chatbot-llm.onrender.com/api/v1/vector/upsert/a9dce05f-2f47-4b25-b18e-57b65b423ca0',
    "json": 'https://sales-ai-chatbot-llm.onrender.com/api/v1/vector/upsert/3e7d998e-f502-4c64-95ec-2de99b4b086d',
    "text": 'https://sales-ai-chatbot-llm.onrender.com/api/v1/vector/upsert/29667912-fff7-4e2c-aa4e-f836c4fdb7f4'
}
extension_list = ["csv", "docx", "pdf", "json"]


async def embed_file(email = str, name = str, file = File):
    file_contents =  await file.read()
    file_extension = file.filename.split('.')[-1].lower()
    file_to_send = ("files", (file.filename, file_contents, file.content_type))
    file_name = file.filename
    print(LLM_BEARER_TOKEN)
    headers = {
        "Authorization": f"Bearer {LLM_BEARER_TOKEN}="
    }

    data = {
        "pineconeNamespace": f"{email}-{name}",
        "tableName": f"{email}-{name}",
        "namespace": f"{email}-{name}",
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
        return {'success': 'Upsert vector DB'}
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))
    


async def embed_text(email = str, name = str, text = str):
    print(LLM_BEARER_TOKEN)
    headers = {
        "Authorization": f"Bearer {LLM_BEARER_TOKEN}="
    }

    json_data = {
        "overrideConfig": {
            "text": text,
            "metadata": {
                "source": "plainText"
            },
            "tableName": f"{email}-{name}",
            "namespace": f"{email}-{name}",
        }
    }
    # data = {
    #     "pineconeNamespace": f"{email}-{name}",
    #     "tableName": f"{email}-{name}",
    #     "namespace": f"{email}-{name}",
    #     "metadata": f'{{"source": "{file_name}"}}'
    # }
    # print(data)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=30.0)) as client:
            api_response = await client.post(
                LLM_API_URL["text"],
                headers=headers,
                json=json_data,
            )
            print("API Response:", api_response)
            print("Response Status Code:", api_response.status_code)
            print("Response Content:", api_response.text)
        if api_response.status_code != 200:
            print("here")  # Adjust `200` if your API uses different success codes
            raise HTTPException(status_code=api_response.status_code, detail="Error Occurred")
        return {'success': 'Upsert vector DB'}
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))