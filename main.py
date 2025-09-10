from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

app = FastAPI(
    title="AI JSON Prompt Generator API",
    description="FastAPI application that generates structured JSON prompts for LLMs from natural language descriptions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI JSON Prompt Generator API",
        "version": "1.0.0",
        "python_version": sys.version,
        "python_path": sys.path[:3],  # First 3 paths only
        "current_dir": os.getcwd(),
        "environment": "leapcell_deployment"
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to AI JSON Prompt Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "deployment_test_mode",
        "description": "Testing deployment - full features will be enabled once dependencies are verified",
        "available_endpoints": {
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "API is working!",
        "status": "success",
        "deployment": "leapcell",
        "next_step": "Enable full AI prompt generation features"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
