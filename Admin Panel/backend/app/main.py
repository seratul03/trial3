"""
Main FastAPI application
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import logging

from app.database import init_db
from app.scheduler import start_scheduler, shutdown_scheduler
from app.routes import auth, kb, subjects, queries, announcements, analytics, feedback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting up application...")
    init_db()
    start_scheduler()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    shutdown_scheduler()
    logger.info("Application shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="College Chatbot Admin Panel API",
    description="Backend API for teacher/admin panel to manage chatbot knowledge base",
    version="1.0.0",
    lifespan=lifespan
)

# CORS is handled by the custom middleware `echo_origin_middleware` below.

# Additional small middleware to ensure when credentialed requests are used
# we echo the specific Origin value (browsers reject Access-Control-Allow-Origin: *
# together with Access-Control-Allow-Credentials: true). This middleware will
# set the Access-Control-Allow-Origin to the request Origin when it's in our
# allowlist and will add the standard CORS response headers for preflight.
ALLOWED_ORIGINS = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
}


@app.middleware("http")
async def echo_origin_middleware(request: Request, call_next):
    origin = request.headers.get("origin")

    # Handle preflight OPTIONS quickly
    if request.method == "OPTIONS":
        from fastapi.responses import PlainTextResponse
        resp = PlainTextResponse("")
    else:
        resp = await call_next(request)

    # Only set credentialed CORS headers when origin is allowed
    if origin and origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Expose-Headers"] = ",".join(["*"])
        # Allow requested headers (if any) or default to common headers
        acrh = request.headers.get("access-control-request-headers")
        resp.headers["Access-Control-Allow-Headers"] = acrh if acrh else "Authorization,Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,PATCH,OPTIONS"

    return resp


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "data": None
        }
    )


# Include routers
app.include_router(auth.router)
app.include_router(kb.router)
app.include_router(subjects.router)
app.include_router(queries.router)
app.include_router(announcements.router)
app.include_router(analytics.router)
app.include_router(feedback.router)

# Mount uploads directory for static file serving
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Serve frontend static files from the project `frontend` directory so the
# backend and frontend are available on the same origin/port (no CORS needed).
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    logger.warning("Frontend directory not found at %s, skipping static mount", FRONTEND_DIR)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Admin Panel API is running"}


# Handle OPTIONS requests explicitly for CORS preflight
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {"message": "OK"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
