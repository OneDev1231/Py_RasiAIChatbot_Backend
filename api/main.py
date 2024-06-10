from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .app.router import auth as auth
from .app.router import upsert as upsert

import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

allowed_origins = os.getenv("ALLOWED_ORIGINS").split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(upsert.router, tags=["upsert"])

# define the route:
@app.get("/", tags=["root"])

def root():
    return {"message": "Hello World"}

# define the entry point. In the entry point, using uvicorn to run server
if __name__ == "__main__":
    uvicorn.run("app", host="0.0.0.0", port=8000, reload=True)