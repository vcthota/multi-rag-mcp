"""
Multi-RAG AI Automation Platform
Main FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import logging
import time

from src.config.settings import get_settings
from src.api.v1.routes import api_router
from src.core.utils.logger import setup_logging
from src.core.exceptions import MultiRAGException
from src.api.middleware.error_handler import error_handler_middleware, custom_exception_handler

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Multi-RAG AI Automation Platform")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize connections
    # await init_vector_db()
    # await init_database()
    # await init_redis()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-RAG AI Automation Platform")
    # await close_connections()


# Create FastAPI application
app = FastAPI(
    title="Multi-RAG AI Automation Platform",
    description="""
    Unified AI automation platform for:
    - API Governance (validation & correction)
    - GraphQL Schema Validation
    - Real-time Log Classification
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add error handler middleware
@app.middleware("http")
async def add_error_handler(request: Request, call_next):
    """Add error handling middleware"""
    return await error_handler_middleware(request, call_next)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom exception handlers
app.add_exception_handler(MultiRAGException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, custom_exception_handler)
app.add_exception_handler(StarletteHTTPException, custom_exception_handler)


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "multi-rag-platform"}


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint"""
    # TODO: Check dependencies (DB, Redis, Vector DB)
    return {"status": "ready", "service": "multi-rag-platform"}


# Fallback exception handler for any unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global fallback exception handler"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Unhandled exception: {exc}",
        extra={"request_id": request_id, "path": request.url.path},
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
                "request_id": request_id
            }
        }
    )


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Multi-RAG AI Automation Platform",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "services": {
            "api_governance": "/api/v1/governance",
            "graphql_validator": "/api/v1/graphql",
            "log_classifier": "/api/v1/logs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
