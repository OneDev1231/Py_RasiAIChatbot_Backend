
from fastapi import File, HTTPException
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client
from dotenv import load_dotenv
import httpx

import os
load_dotenv()

# LLM_BEARER_TOKEN = os.getenv("LLM_BEARER_TOKEN")
LLM_API_URL = {
    "csv": 'https://llm.rasi.ai/api/v1/upsert_csv/',
    "docx": 'https://llm.rasi.ai/api/v1/upsert_doc/',
    "pdf": 'https://llm.rasi.ai/api/v1/upsert_pdf/',
    "json": 'https://llm.rasi.ai/api/v1/upsert_json/',
    "txt": 'https://llm.rasi.ai/api/v1/upsert_txt/',
    "xlsx": 'https://llm.rasi.ai/api/v1/upsert_excel/',
    "pptx": 'https://llm.rasi.ai/api/v1/upsert_ppt/',
}

LLM_API_URL_TEST = {
    "csv": 'http://localhost:4003/api/v1/upsert_csv/',
    "docx": 'http://localhost:4003/api/v1/upsert_doc/',
    "pdf": 'http://localhost:4003/api/v1/upsert_pdf/',
    "json": 'http://localhost:4003/api/v1/upsert_json/',
    "txt": 'http://localhost:4003/api/v1/upsert_txt/',
    "xlsx": 'http://localhost:4003/api/v1/upsert_excel/',
    "pptx": 'http://localhost:4003/api/v1/upsert_ppt/',
}

extension_list = ["csv", "docx", "pdf", "json", "txt", "xlsx", "pptx"]



async def embed_file(chatbot_name = str, file = File, token = str):
    # LLM_BEARER_TOKEN = token
    # file_contents =  await file.read()
    # file_extension = file.filename.split('.')[-1].lower()
    # file_to_send = {
    #     "files", (file.filename, file_contents, file.content_type)
    # }
    # headers = {
    #     "Authorization": f"Bearer {LLM_BEARER_TOKEN}"
    # }

    # data = {
    #     "index_name": chatbot_name
    # }
    # print(data)
    # try:
    #     print(LLM_API_URL[file_extension])
    #     async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=30.0)) as client:
    #         api_response = await client.post(
    #             LLM_API_URL_TEST[file_extension],
    #             headers=headers,
    #             data=data,
    #             files=file_to_send
    #         )
    #         print("API Response:", api_response)
    #         print("Response Status Code:", api_response.status_code)
    #         print("Response Content:", api_response.json())
    #     if api_response.status_code != 200:
    #         print(api_response.content)  # Adjust `200` if your API uses different success codes
    #         raise HTTPException(status_code=api_response.status_code, detail=api_response.content)
    #     return {'success': 'Upsert vector DB'}
    # except Exception as e:
    #     raise HTTPException(status_code=501, detail=str(e))
    LLM_BEARER_TOKEN = token
    try:
        # Read file contents
        file_contents = await file.read()
        file_extension = file.filename.split('.')[-1].lower()

        # Define headers, data, and files for HTTP request
        headers = {
            "Authorization": f"Bearer {LLM_BEARER_TOKEN}",
        }
        print(headers)

        data = {
            "index_name": chatbot_name
        }

        files = {"file": (file.filename, file_contents, file.content_type)}
        print(data)

        if file_extension not in LLM_API_URL:
            raise HTTPException(status_code=400, detail="Unsupported file extension")

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=30.0)) as client:
            api_response = await client.post(
                LLM_API_URL[file_extension],
                headers=headers,
                data=data,
                files=files
            )

            print("API Response:", api_response)
            print("Response Status Code:", api_response.status_code)
            print("Response Content:", api_response.json())

            if api_response.status_code != 200:
                print(api_response.content)  # Adjust `200` if your API uses different success codes
                # Raise HTTPException with the exact status code and response content
                raise HTTPException(status_code=api_response.status_code, detail=api_response.text)

            return {'success': 'Upsert vector DB'}
      
    except HTTPException as e:
        print(f"Caught HTTPException: Status Code: {e.status_code}, Detail: {e.detail}")
        raise e  # Reraise HTTP exceptions as-is
    except Exception as e:
        print(f"Caught General Exception: {str(e)}")
        raise HTTPException(status_code=501, detail=str(e))  # Handle general exceptions separately
    


async def embed_text(name = str, text = str, token = str):
    LLM_BEARER_TOKEN = token
    headers = {
        "Authorization": f"Bearer {LLM_BEARER_TOKEN}"
    }

    json_data = {
        "overrideConfig": {
            "text": text,
            "metadata": {
                "source": "plainText"
            },
            "tableName": f"{token}-{name}",
            "namespace": f"{token}-{name}",
        }
    }
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