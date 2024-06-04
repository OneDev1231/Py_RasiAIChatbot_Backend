from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_ANON_PUBLIC_KEY = os.getenv("SUPABASE_ANON_PUBLIC_KEY")


router = APIRouter()

class SignUpRequest(BaseModel):
    userName: str
    email: str
    password: str

class SignInRequest(BaseModel):
    email: str
    password: str

@router.post("/signup/")
async def signup(request: SignUpRequest):
    async with httpx.AsyncClient() as client:    
        response = await client.post(
            f"{SUPABASE_PROJECT_URL}/auth/v1/signup",
            json={"email": request.email, "password": request.password, "data": {"username": request.userName}},
            headers={"apikey": SUPABASE_ANON_PUBLIC_KEY, "Authorization": f"Bearer {SUPABASE_ANON_PUBLIC_KEY}"},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()

@router.post("/signin/")
async def signin(request: SignInRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_PROJECT_URL}/auth/v1/token?grant_type=password",
            json={"email": request.email, "password": request.password},
            headers={"apikey": SUPABASE_ANON_PUBLIC_KEY, "Authorization": f"Bearer {SUPABASE_ANON_PUBLIC_KEY}"},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()