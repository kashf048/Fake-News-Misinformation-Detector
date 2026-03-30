"""
Main FastAPI Application
Fake News & Misinformation Detector API
"""

import os
import logging
from rich.logging import RichHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.database import connect_to_mongo, close_mongo_connection
from app.services.ai_models import AIModels
from app.routes.analysis import router as analysis_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)]
)
logger = logging.getLogger("fake_news_api")

# Silence redundant uvicorn logging or redirect it to Rich
for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
    uv_logger = logging.getLogger(name)
    uv_logger.handlers = [RichHandler(rich_tracebacks=True, markup=True)]
    uv_logger.propagate = False

# Create FastAPI app
app = FastAPI(
    title="Fake News & Misinformation Detector",
    description="Multimodal AI system for detecting fake news and misinformation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

logger.info(f"[bold blue]CORS Allowed Origins:[/bold blue] {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    try:
        logger.info("Starting up Fake News Detector API...")
        
        # Connect to MongoDB
        await connect_to_mongo()
        
        # Initialize AI models
        await AIModels.initialize_models()
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        logger.info("Shutting down Fake News Detector API...")
        await close_mongo_connection()
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Fake News & Misinformation Detector API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }


@app.get("/api/status")
async def status():
    """API status endpoint"""
    return {
        "status": "healthy",
        "service": "Fake News Detector API",
        "version": "1.0.0",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
