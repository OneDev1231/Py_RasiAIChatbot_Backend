from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Depends, Response, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_ANON_PUBLIC_KEY = os.getenv("SUPABASE_ANON_PUBLIC_KEY")


router = APIRouter()
supabase: Client = create_client(SUPABASE_PROJECT_URL, SUPABASE_ANON_PUBLIC_KEY)

class SignUpRequest(BaseModel):
    userName: str
    email: str
    password: str

class SignInRequest(BaseModel):
    email: str
    password: str

@router.post("/signup/")
def signup(request: SignUpRequest):
    try:
        response_signup = supabase.auth.sign_up({
            'email': request.email,
            'password': request.password,
        })
        print("User signed up:", response_signup)
        try:
            data = {
                "id": response_signup.user.id,
                "name": request.userName,
                "email": request.email,
            }
            response = supabase.table("business_owner").insert(data).execute()
            print("Row added: ", response.data)
            return response
        except Exception as e:
            print("Error:", e)
            return e
    except Exception as e:
        print("Error during sign-up:", e)
        return e

@router.post("/signin/")
def signin(request: SignInRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            'email': request.email,
            'password': request.password,
        })
        # print("User signed in:", response)
        resp = JSONResponse(content={
            "message": "User signed in successfully",
            "user_id": response.user.id,
        })
        is_production = os.getenv("ENV") == "production"
        print(is_production)
        if is_production:
            resp.set_cookie(
                key="access_token",
                value=response.session.access_token,
                httponly=False,
                secure=True,
                samesite="Lax",
                domain='.rasi.ai',
            )
            resp.set_cookie(
                key="refresh_token",
                value=response.session.refresh_token,
                httponly=False,
                secure=True,
                samesite="Lax",
                domain='.rasi.ai',
            )
        else:
            resp.set_cookie(
                key="access_token",
                value=response.session.access_token,
                httponly=False,
                secure=False,
                samesite="Lax",
            )
            resp.set_cookie(
                key="refresh_token",
                value=response.session.refresh_token,
                httponly=False,
                secure=False,
                samesite="Lax",
            )
        print(resp)
        return resp
        # Access token and user information can be accessed via response
        # access_token = response['data']['access_token']
        # print("Access Token:", access_token)
    except Exception as e:
        print(e)
        return e

@router.post("/refresh")
def refresh_token(response: Response, refresh_token: Optional[str] = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    refresh_response = supabase.auth.refresh_session(refresh_token).model_dump()
    print(refresh_response)
    print(type(refresh_response))
    if refresh_response.get("error"):
        raise HTTPException(status_code=401, detail=refresh_response["error"]["message"])
    
    new_access_token = refresh_response['session']['access_token']
    new_refresh_token = refresh_response['session']['refresh_token']
    print(new_access_token)
    resp = JSONResponse(content={"message": "Token refreshed"})
    resp.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=True, samesite="Lax")
    resp.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, secure=True, samesite="Lax")
    return resp