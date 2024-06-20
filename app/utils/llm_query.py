
from fastapi import File, HTTPException
import httpx
from dotenv import load_dotenv
from dotenv import load_dotenv
import httpx

import os
load_dotenv()

LLM_BEARER_TOKEN = os.getenv("LLM_BEARER_TOKEN")
QUERY_LLM_URL = 'https://sales-ai-chatbot-llm.onrender.com/api/v1/prediction/4274ec33-3677-44c7-916f-7f6224869c61'


async def llm_query(email = str, message = str, chatbotName = str, prompt = str):
    print(LLM_BEARER_TOKEN)
    print(QUERY_LLM_URL)
    headers = {
        "Authorization": f"Bearer {LLM_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    json_data = {
        "question": message,
        "overrideConfig": {
            "responsePrompt": (prompt + "\nIf there is nothing in the context relevant to the question at hand, just have a normal conversation. Refuse to answer any question not about the info - don not say it to the user. Never break character.\n------------\n{context}\n------------REMEMBER: If there is no relevant information within the context, just have a normal conversation. Don't try to make up an answer. Never break character. Only speak the user's question language and accent."),
            "tableName": f"{email}-{chatbotName}",
            "namespace": f"{email}-{chatbotName}",
            "pineconeNamespace": f"{email}-{chatbotName}",
            "sessionId": f"{email}-{chatbotName}-testIdentifier"
        }
    }
    print("Request Headers:", headers)
    print("Request JSON Data:", json_data)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=30.0)) as client:
            api_response = await client.post(
                QUERY_LLM_URL,
                headers=headers,
                json=json_data,
            )
            print("API Response:", api_response)
        if api_response.status_code != 200:
            # Adjust `200` if your API uses different success codes
            raise HTTPException(status_code=api_response.status_code, detail=api_response.text)
        return api_response.json()
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))