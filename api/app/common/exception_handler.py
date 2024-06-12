from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

async def custom_http_exception_handler(request: Request, exc: HTTPException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

    updated_access_token = request.state.updated_access_token
    updated_refresh_token = request.state.updated_refresh_token
    if updated_access_token:
        response.set_cookie(key="access_token", value=updated_access_token)
    if updated_refresh_token:
        response.set_cookie(key="refresh_token", value=updated_refresh_token)
    return response