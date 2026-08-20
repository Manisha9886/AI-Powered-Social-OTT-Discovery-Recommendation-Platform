import os
import sys
from dotenv import load_dotenv

# Ensure root directory and backend directory are in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(backend_dir)

for path in [root_dir, backend_dir, current_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

load_dotenv()

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1 import api_router
from app.db.init_db import init_db

# Initialize Database tables
try:
    init_db()
except Exception as e:
    print(f"Database initialization warning: {e}")

app = FastAPI(
    title="OTT Discovery API",
    description="API for the AI-Powered Social OTT Discovery & Recommendation Platform",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")
