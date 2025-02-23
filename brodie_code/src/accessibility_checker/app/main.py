from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from accessibility_checker.app.api.routes import router as api_router

app = FastAPI(title="PDF Accessibility Processor")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory where main.py is located
current_dir = Path(__file__).resolve().parent
static_dir = current_dir / "static"

# Verify static directory exists
if not static_dir.exists():
    raise RuntimeError(f"Static directory not found at {static_dir}")

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    """Redirect root to the static index.html"""
    return RedirectResponse(url="/static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}
