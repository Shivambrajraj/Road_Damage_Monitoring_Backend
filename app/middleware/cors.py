# backend/app/middleware/cors.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI) -> None:
    # 1. Define exact allowed origins (NO trailing slashes!)
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://road-damage-monitoring-frontend.vercel.app",
    ]

    # 2. Optional: Allow all Vercel preview deployments for your project
    origin_regex = r"https://road-damage-monitoring-frontend.*\.vercel\.app"

    # 3. Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=origin_regex,
        allow_credentials=True,
        allow_methods=["*"],  # Allows GET, POST, PUT, DELETE, OPTIONS, PATCH
        allow_headers=["*"],  # Allows Authorization, Content-Type, etc.
    )