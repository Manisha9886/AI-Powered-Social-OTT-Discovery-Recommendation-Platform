import os
import sys
import ssl

# Register both project root and backend directory in sys.path for universal module imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


from dotenv import load_dotenv
load_dotenv()

# Bypass SSL verification only in development (e.g. Windows dev machines with local proxy/certs)
if os.getenv("ENVIRONMENT", "development") == "development":
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
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")
