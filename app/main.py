"""
AI Banking Assistant - Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent banking assistant with RAG and tool integration",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix=settings.API_V1_STR, tags=["chat"])

@app.get("/")
async def root():
    return {"message": "AI Banking Assistant API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}