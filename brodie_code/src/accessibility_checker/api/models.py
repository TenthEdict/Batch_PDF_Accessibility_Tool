from dataclasses import dataclass
from typing import Dict, Optional, Any

@dataclass
class ProcessingResult:
    filename: str
    status: str
    violations: int
    processed_path: Optional[str] = None
    details: Dict[str, Any] = None