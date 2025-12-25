"""
FastAPI main application entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, logger
from app.models import CampaignResponse
from app.services.campaign_orchestrator import CampaignOrchestrator
from app.services.email_service import EmailService

# Application state
campaign_status = {
    "running": False,
    "last_result": None
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("=" * 80)
    logger.info("AI SALES CAMPAIGN CRM - STARTING UP")
    logger.info("=" * 80)
    logger.info(f"LLM Model: {settings.llm_model}")
    logger.info(f"SMTP Host: {settings.smtp_host}:{settings.smtp_port}")
    logger.info(f"Max Concurrent Leads: {settings.max_concurrent_leads}")
    
    # Test email connection
    try:
        email_service = EmailService()
        connection_ok = await email_service.test_connection()
        if connection_ok:
            logger.info("✓ SMTP connection test passed")
        else:
            logger.warning("⚠ SMTP connection test failed - emails may not send")
    except Exception as e:
        logger.error(f"✗ SMTP connection test error: {e}")
    
    logger.info("Application ready to accept requests")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="AI Sales Campaign CRM",
    description="AI-powered lead scoring, enrichment, and outreach automation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Sales Campaign CRM",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "run_campaign": "/campaign/run",
            "campaign_status": "/campaign/status",
            "docs": "/docs"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and configuration info.
    """
    try:
        return {
            "status": "healthy",
            "timestamp": str(datetime.now()),
            "config": {
                "llm_model": settings.llm_model,
                "smtp_host": settings.smtp_host,
                "max_concurrent_leads": settings.max_concurrent_leads
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Campaign status endpoint
@app.get("/campaign/status")
async def get_campaign_status():
    """
    Get current campaign status.
    
    Returns whether a campaign is running and last result.
    """
    return {
        "running": campaign_status["running"],
        "last_result": campaign_status["last_result"]
    }

# Main campaign execution endpoint
@app.post("/campaign/run", response_model=CampaignResponse)
async def run_campaign(background_tasks: BackgroundTasks):
    """
    Execute the complete campaign pipeline.
    
    This endpoint:
    1. Reads leads from CSV
    2. Scores and enriches leads using LLM
    3. Generates personalized emails
    4. Sends emails via SMTP
    5. Simulates responses
    6. Generates campaign report
    
    Returns:
        CampaignResponse with stats and file paths
    """
    # Check if campaign is already running
    if campaign_status["running"]:
        raise HTTPException(
            status_code=409,
            detail="Campaign is already running. Please wait for it to complete."
        )
    
    try:
        # Mark campaign as running
        campaign_status["running"] = True
        logger.info("Campaign execution requested via API")
        
        # Initialize orchestrator
        orchestrator = CampaignOrchestrator()
        
        # Run campaign
        result = await orchestrator.run_campaign()
        
        # Store result
        campaign_status["last_result"] = result.dict()
        campaign_status["running"] = False
        
        logger.info("Campaign execution completed via API")
        return result
        
    except Exception as e:
        campaign_status["running"] = False
        logger.error(f"Campaign execution error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Campaign execution failed: {str(e)}"
        )

# Quick test endpoint
@app.get("/test/smtp")
async def test_smtp_connection():
    """
    Test SMTP connection to MailHog.
    
    Returns connection status.
    """
    try:
        email_service = EmailService()
        connection_ok = await email_service.test_connection()
        
        if connection_ok:
            return {
                "status": "success",
                "message": "SMTP connection successful",
                "smtp_host": settings.smtp_host,
                "smtp_port": settings.smtp_port
            }
        else:
            return {
                "status": "failed",
                "message": "SMTP connection failed",
                "smtp_host": settings.smtp_host,
                "smtp_port": settings.smtp_port
            }
    except Exception as e:
        logger.error(f"SMTP test error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

# Import datetime for health check
from datetime import datetime

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )