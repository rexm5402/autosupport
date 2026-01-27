from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import router as api_router
from app.ml.inference import MLService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global ML service instance
ml_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    logger.info("Starting AutoSupport API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Initialize ML service
    global ml_service
    ml_service = MLService()
    await ml_service.load_models()
    logger.info("ML models loaded successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AutoSupport API...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Customer Support Ticket Routing & Insight System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AutoSupport API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "ml_models": "loaded" if ml_service and ml_service.is_ready() else "not loaded"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "type": type(exc).__name__
        }
    )


# Make ml_service accessible to other modules
def get_ml_service() -> MLService:
    """Get the global ML service instance"""
    if ml_service is None:
        raise HTTPException(status_code=503, detail="ML service not initialized")
    return ml_service
