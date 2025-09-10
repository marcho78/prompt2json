from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys

# Try to import our full application components
try:
    from src.config import settings
    print(f"✅ Settings loaded successfully")
    
    # Try database initialization
    try:
        from src.models.database import create_tables
        DATABASE_COMPONENTS = True
        print(f"✅ Database components loaded")
        # Get database URL for display only - don't fail if not available
        try:
            database_url = settings.get_database_url()
            print(f"📁 Database URL configured: PostgreSQL connection")
        except:
            database_url = "DATABASE_URL not set"
            print(f"⚠️  DATABASE_URL environment variable not set")
    except Exception as db_error:
        print(f"⚠️  Database components failed to load: {db_error}")
        DATABASE_COMPONENTS = False
        database_url = "not_available"
    
    # Try to load API routes
    try:
        from src.api.routes import generate, optimize, templates, test, analyze, convert, merge, auth, usage
        ROUTES_AVAILABLE = True
        print(f"✅ API routes loaded successfully")
    except Exception as routes_error:
        print(f"⚠️  API routes failed to load: {routes_error}")
        ROUTES_AVAILABLE = False
    
    FULL_APP_AVAILABLE = DATABASE_COMPONENTS and ROUTES_AVAILABLE
    
    # Create database tables on startup (with error handling)
    if DATABASE_COMPONENTS:
        try:
            print(f"📋 Creating database tables...")
            create_tables()
            DATABASE_READY = True
            print(f"✅ Database initialized successfully")
        except Exception as e:
            print(f"⚠️  Database initialization warning: {e}")
            DATABASE_READY = False
            # Don't fail completely - app can still run for basic health checks
    else:
        DATABASE_READY = False
        print(f"⚠️  Database not available - app running in limited mode")
        
except ImportError as e:
    print(f"❌ Full app imports failed: {e}")
    print("🔄 Running in fallback mode...")
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
if FULL_APP_AVAILABLE and ROUTES_AVAILABLE:
    print(f"🚀 Loading full application routes...")
    try:
        app.include_router(auth.router, prefix="/auth", tags=["authentication"])
        app.include_router(generate.router, prefix="/api/v1", tags=["prompt-generation"])
        app.include_router(optimize.router, prefix="/api/v1", tags=["prompt-optimization"])  
        app.include_router(convert.router, prefix="/api/v1", tags=["prompt-conversion"])
        app.include_router(templates.router, prefix="/api/v1", tags=["templates"])
        app.include_router(test.router, prefix="/api/v1", tags=["prompt-testing"])
        app.include_router(analyze.router, prefix="/api/v1", tags=["prompt-analysis"])
        app.include_router(merge.router, prefix="/api/v1", tags=["prompt-merging"])
        app.include_router(usage.router, prefix="/api/v1", tags=["usage-monitoring"])
        print(f"✅ All routes loaded successfully")
    except Exception as route_error:
        print(f"❌ Route loading failed: {route_error}")
        FULL_APP_AVAILABLE = False
else:
    print(f"⚠️  Running with fallback routes only")
    # Fallback: Basic endpoints for testing
    @app.get("/api/v1/status")
    async def fallback_status():
        return {
            "status": "running_fallback_mode", 
            "message": "Full AI features unavailable - check deployment configuration",
            "missing_features": ["authentication", "prompt_generation", "rate_limiting"]
        }

# Test endpoint - always works
@app.get("/api/v1/test")
async def test_endpoint():
    """Simple test endpoint that always works"""
    return {
        "status": "ok",
        "message": "API is responding",
        "timestamp": "2025-01-10T21:40:00Z",
        "test_passed": True
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
        "database_type": "PostgreSQL" if FULL_APP_AVAILABLE and database_url != "DATABASE_URL not set" else "not_configured",
        "environment": "leapcell_serverless",
        "writable_dir": "/tmp" if not os.access('.', os.W_OK) else os.getcwd()
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
            "database_ready": DATABASE_READY,
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
            "status": "fallback_mode",
            "description": "API running in fallback mode - full AI features unavailable",
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
