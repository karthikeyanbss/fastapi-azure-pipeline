"""
FastAPI Application for Azure Container Apps Deployment Demo
Supports multi-environment deployment (Dev, QA, Prod)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Azure Multi-Environment Demo",
    description="Professional-grade API deployed across Dev, QA, and Prod environments",
    version="1.0.0"
)

# Environment configuration
APP_ENV = os.getenv("APP_ENV", "local")
DEPLOYED_AT = os.getenv("DEPLOYED_AT", "unknown")
GIT_SHA = os.getenv("GIT_SHA", "unknown")


class HealthResponse(BaseModel):
    status: str
    environment: str
    deployed_at: str
    git_sha: str
    timestamp: str


class EchoRequest(BaseModel):
    message: str


class EchoResponse(BaseModel):
    original_message: str
    environment: str
    echoed_at: str


@app.get("/")
async def root():
    """Root endpoint with environment information"""
    return {
        "message": f"Welcome to FastAPI on Azure Container Apps!",
        "environment": APP_ENV,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for container orchestration
    Returns 200 OK when the service is healthy
    """
    return HealthResponse(
        status="healthy",
        environment=APP_ENV,
        deployed_at=DEPLOYED_AT,
        git_sha=GIT_SHA,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/info")
async def app_info():
    """Get detailed application and environment information"""
    return {
        "application": {
            "name": "FastAPI Azure Demo",
            "version": "1.0.0",
            "environment": APP_ENV
        },
        "deployment": {
            "deployed_at": DEPLOYED_AT,
            "git_sha": GIT_SHA
        },
        "runtime": {
            "python_version": os.sys.version,
            "timestamp": datetime.utcnow().isoformat()
        }
    }


@app.post("/echo", response_model=EchoResponse)
async def echo_message(request: EchoRequest):
    """
    Echo endpoint that returns the message with environment context
    Useful for testing environment-specific behavior
    """
    logger.info(f"[{APP_ENV}] Echo request received: {request.message}")
    
    return EchoResponse(
        original_message=request.message,
        environment=APP_ENV,
        echoed_at=datetime.utcnow().isoformat()
    )


@app.get("/environment")
async def get_environment():
    """
    Returns all environment variables (useful for debugging)
    In production, you might want to filter sensitive values
    """
    if APP_ENV == "prod":
        raise HTTPException(
            status_code=403,
            detail="Environment variables are not exposed in production"
        )
    
    # Only show non-sensitive environment variables
    safe_env_vars = {
        k: v for k, v in os.environ.items()
        if not any(sensitive in k.lower() for sensitive in ['key', 'secret', 'password', 'token'])
    }
    
    return {
        "environment": APP_ENV,
        "variables": safe_env_vars
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "environment": APP_ENV,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # For local development
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )