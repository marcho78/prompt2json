from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

# Try to import our full application components
try:
    from src.config import settings
    from src.models.database import create_tables
    from src.api.routes import generate, optimize, templates, test, analyze, convert, merge, auth, usage
    FULL_APP_AVAILABLE = True
    
    # Create database tables on startup (with error handling)
    try:
        create_tables()
        DATABASE_READY = True
    except Exception as e:
        print(f"Database initialization warning: {e}")
        DATABASE_READY = False
        
except ImportError as e:
    print(f"Full app imports failed: {e}")
    print("Running in basic mode...")
    FULL_APP_AVAILABLE = False
    DATABASE_READY = False
    
    # Fallback settings
    class FallbackSettings:
        APP_NAME = "AI JSON Prompt Generator API"
        VERSION = "1.0.0"
        DEBUG = True
        HOST = "0.0.0.0"
        PORT = 8080
        ALLOWED_ORIGINS = ["*"]
    
    settings = FallbackSettings()

app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI application that generates structured JSON prompts for LLMs from natural language descriptions",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (conditional based on availability)
if FULL_APP_AVAILABLE:
    app.include_router(auth.router, prefix="/auth", tags=["authentication"])
    app.include_router(generate.router, prefix="/api/v1", tags=["prompt-generation"])
    app.include_router(optimize.router, prefix="/api/v1", tags=["prompt-optimization"])  
    app.include_router(convert.router, prefix="/api/v1", tags=["prompt-conversion"])
    app.include_router(templates.router, prefix="/api/v1", tags=["templates"])
    app.include_router(test.router, prefix="/api/v1", tags=["prompt-testing"])
    app.include_router(analyze.router, prefix="/api/v1", tags=["prompt-analysis"])
    app.include_router(merge.router, prefix="/api/v1", tags=["prompt-merging"])
    app.include_router(usage.router, prefix="/api/v1", tags=["usage-monitoring"])
else:
    # Fallback: Basic endpoints for testing
    @app.get("/api/v1/status")
    async def fallback_status():
        return {
            "status": "running_basic_mode", 
            "message": "Full AI features unavailable - check deployment configuration",
            "missing_features": ["authentication", "prompt_generation", "rate_limiting"]
        }

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "full_app_loaded": FULL_APP_AVAILABLE,
        "database_ready": DATABASE_READY if FULL_APP_AVAILABLE else "not_applicable",
        "timestamp": "2025-01-10T19:54:00Z"
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    if FULL_APP_AVAILABLE:
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "description": "Generate structured JSON prompts for LLMs from natural language descriptions",
            "status": "full_features_available",
            "endpoints": {
                "authentication": "/auth",
                "generate_prompt": "/api/v1/generate-prompt",
                "optimize_prompt": "/api/v1/optimize-prompt", 
                "convert_prompt": "/api/v1/convert-prompt",
                "templates": "/api/v1/templates",
                "test_prompt": "/api/v1/test-prompt",
                "analyze_prompt": "/api/v1/analyze-prompt",
                "merge_prompts": "/api/v1/merge-prompts",
                "usage": "/api/v1/usage"
            }
        }
    else:
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "status": "basic_mode",
            "description": "API running in basic mode - full AI features unavailable",
            "available_endpoints": {
                "health": "/health",
                "status": "/api/v1/status"
            },
            "note": "Check deployment configuration for full AI prompt generation features"
        }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
