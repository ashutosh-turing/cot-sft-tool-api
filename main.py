# backend/main.py
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()  
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import problems, websockets
import os

app = FastAPI(
    title="Turing :: Data Pack SFT Platform",
    description="Backend for Turing tasks with Excel, Codeforces, LLM, etc.",
    version="1.0.0",
)


# Configure CORS for your React frontend (update origin for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Change for deployment!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register your routers
app.include_router(problems.router)
app.include_router(websockets.router)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
