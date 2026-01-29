"""
FastAPI application entry point.

This module initializes and configures the FastAPI application,
including middleware, CORS, and route registration.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1 import (
    auth,
    projects,
    crawls,
    analysis,
    list_crawl,
    collaboration,
    dashboards,
    monitoring,
    competitive,
    serp,
    ai,
    advanced_analysis,
    export,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.APP_NAME}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    
    yield
    
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade SEO analysis platform with AI-powered insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add trusted host middleware for production
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # Configure properly in production
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint returning API information."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }


# Include API routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"],
)

app.include_router(
    projects.router,
    prefix=f"{settings.API_V1_PREFIX}/projects",
    tags=["Projects"],
)

app.include_router(
    crawls.router,
    prefix=f"{settings.API_V1_PREFIX}/crawls",
    tags=["Crawls"],
)

app.include_router(
    analysis.router,
    prefix=f"{settings.API_V1_PREFIX}/analysis",
    tags=["Analysis"],
)

app.include_router(
    list_crawl.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["List Mode Crawling"],
)

app.include_router(
    collaboration.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Team Collaboration"],
)

app.include_router(
    dashboards.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Custom Dashboards"],
)

app.include_router(
    monitoring.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Monitoring & Alerts"],
)

app.include_router(
    competitive.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Competitive Analysis"],
)

app.include_router(
    serp.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["SERP Tracking"],
)

app.include_router(
    ai.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["AI-Powered Features"],
)

app.include_router(
    advanced_analysis.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Advanced Analysis"],
)

app.include_router(
    export.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Export & Reporting"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    
    In production, this would log to a monitoring service.
    """
    if settings.DEBUG:
        raise exc
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error",
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
