from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.config import settings
from src.models.database import create_tables
from src.api.routes import generate, optimize, templates, test, analyze, convert, merge, auth, usage

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

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        create_tables()
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        raise

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(generate.router, prefix="/api/v1", tags=["prompt-generation"])
app.include_router(optimize.router, prefix="/api/v1", tags=["prompt-optimization"])  
app.include_router(convert.router, prefix="/api/v1", tags=["prompt-conversion"])
app.include_router(templates.router, prefix="/api/v1", tags=["templates"])
app.include_router(test.router, prefix="/api/v1", tags=["prompt-testing"])
app.include_router(analyze.router, prefix="/api/v1", tags=["prompt-analysis"])
app.include_router(merge.router, prefix="/api/v1", tags=["prompt-merging"])
app.include_router(usage.router, prefix="/api/v1", tags=["usage-monitoring"])

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION
    }

@app.get("/kaithhealthcheck")
@app.get("/kaithheathcheck")
async def leapcell_health_check():
    """Health endpoints for Leapcell reverse proxy probes."""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "description": "Generate structured JSON prompts for LLMs from natural language descriptions",
        "endpoints": {
            "authentication": "/auth",
            "generate_prompt": "/api/v1/generate-prompt",
            "optimize_prompt": "/api/v1/optimize-prompt", 
            "convert_prompt": "/api/v1/convert-prompt",
            "templates": "/api/v1/templates",
            "test_prompt": "/api/v1/test-prompt",
            "analyze_prompt": "/api/v1/analyze-prompt",
            "merge_prompts": "/api/v1/merge-prompts"
        }
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
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
