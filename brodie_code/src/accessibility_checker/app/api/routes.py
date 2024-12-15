# api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import tempfile
import shutil
from pathlib import Path
import logging
from datetime import datetime
from accessibility_checker.app.api.models import ProcessingResponse, ProcessingResult
from accessibility_checker.app.core.processor import process_pdf_file

router = APIRouter()

# Store background jobs
processing_jobs = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_files_background(files: List[Path], job_id: str):
    """Background task to process multiple PDF files."""
    try:
        results = []
        for file_path in files:
            result = await process_pdf_file(file_path)
            results.append(result)

        processing_jobs[job_id].status = "completed"
        processing_jobs[job_id].results = results

    except Exception as e:
        logger.error(f"Background task error: {str(e)}")
        processing_jobs[job_id].status = "failed"

@router.post("/process/", response_model=ProcessingResponse)
async def process_pdfs(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
) -> ProcessingResponse:
    """Process multiple PDF files for accessibility."""
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        temp_dir = Path(tempfile.mkdtemp())
        saved_files = []

        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files are accepted")
            
            file_path = temp_dir / file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file_path)

        processing_jobs[job_id] = ProcessingResponse(
            job_id=job_id,
            status="processing"
        )

        background_tasks.add_task(
            process_files_background,
            saved_files,
            job_id
        )

        return processing_jobs[job_id]

    except Exception as e:
        logger.error(f"Error initiating processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=ProcessingResponse)
async def get_processing_status(job_id: str) -> ProcessingResponse:
    """Get the status of a processing job."""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return processing_jobs[job_id]

@router.get("/download/{file_type}/{filename}")
async def download_file(file_type: str, filename: str):
    """Download processed files or reports."""
    try:
        base_dir = Path("output")
        if file_type == "pdf":
            file_path = base_dir / "processed_pdfs" / filename
        elif file_type == "report":
            file_path = base_dir / "reports" / filename
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/pdf' if file_type == "pdf" else 'application/json'
        )

    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
