from dataclasses import dataclass
from typing import Dict, Any
import yaml

@dataclass
class OCRConfig:
    language: str
    psm: int
    oem: int
    char_whitelist: str
    additional_params: Dict[str, Any]

@dataclass
class ProcessingConfig:
    max_workers: int
    batch_size: int
    timeout: int
    retry_count: int
    ocr_settings: OCRConfig
    
class ConfigurationManager:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
            
    def get_ocr_config(self) -> OCRConfig:
        ocr_settings = self._config.get('ocr', {})
        return OCRConfig(
            language=ocr_settings.get('language', 'eng'),
            psm=ocr_settings.get('psm', 3),
            oem=ocr_settings.get('oem', 3),
            char_whitelist=ocr_settings.get('char_whitelist', ''),
            additional_params=ocr_settings.get('additional_params', {})
        )
    
    def get_processing_config(self) -> ProcessingConfig:
        return ProcessingConfig(
            max_workers=self._config.get('max_workers', 4),
            batch_size=self._config.get('batch_size', 10),
            timeout=self._config.get('timeout', 300),
            retry_count=self._config.get('retry_count', 3),
            ocr_settings=self.get_ocr_config()
        )