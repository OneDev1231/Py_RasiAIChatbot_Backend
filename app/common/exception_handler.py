import os
from dotenv import load_dotenv
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

load_dotenv()

async def custom_http_exception_handler(request: Request, exc: HTTPException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

    updated_access_token = request.state.updated_access_token
    updated_refresh_token = request.state.updated_refresh_token
    if updated_access_token and updated_refresh_token:
        is_production = os.getenv("ENV") == "production"
        print(is_production)
        if is_production:
            response.set_cookie(
                key="access_token",
                value=updated_access_token,
                httponly=False,
                secure=True,
                samesite="Lax",
                domain='.rasi.ai',
            )
            response.set_cookie(
                key="refresh_token",
                value=updated_refresh_token,
                httponly=False,
                secure=True,
                samesite="Lax",
                domain='.rasi.ai',
            )
        else:
            response.set_cookie(
                key="access_token",
                value=updated_access_token,
                httponly=False,
                secure=False,
                samesite="Lax",
            )
            response.set_cookie(
                key="refresh_token",
                value=updated_refresh_token,
                httponly=False,
                secure=False,
                samesite="Lax",
            )
   
    return response