# api/models.py
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ProcessingResult(BaseModel):
    filename: str
    status: str
    violations: int
    details: Optional[Dict] = None
    processed_path: Optional[str] = None

class ProcessingResponse(BaseModel):
    job_id: str
    status: str
    results: Optional[List[ProcessingResult]] = None
    timestamp: datetime = datetime.now()
