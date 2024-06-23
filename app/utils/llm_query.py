
from fastapi import File, HTTPException
import httpx
from dotenv import load_dotenv
from dotenv import load_dotenv
import httpx

import os
load_dotenv()

# LLM_BEARER_TOKEN = os.getenv("LLM_BEARER_TOKEN")
QUERY_LLM_URL = 'https://llm.rasi.ai/api/v1/query_llm/'


async def llm_query(customer_id = str, message = str, chatbot_name = str, prompt = str, token = str):
    LLM_BEARER_TOKEN = token
    headers = {
        "Authorization": f"Bearer {LLM_BEARER_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    form_data = {
        "query": message,
        "prompt": prompt,
        "index_name": chatbot_name,
        "thread_id": customer_id
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=30.0)) as client:
            api_response = await client.post(
                QUERY_LLM_URL,
                headers=headers,
                data=form_data,
            )
            print("API Response:", api_response)
        if api_response.status_code != 200:
            # Adjust `200` if your API uses different success codes
            raise HTTPException(status_code=api_response.status_code, detail=api_response.text)
        return api_response.json()
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))