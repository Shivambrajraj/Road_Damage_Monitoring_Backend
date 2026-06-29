# backend/app/middleware/cors.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI) -> None:
    # 1. Define the allowed frontend origins
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # 2. Add the middleware to the FastAPI application instance
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 