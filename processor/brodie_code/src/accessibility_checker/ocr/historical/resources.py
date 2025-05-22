#!/usr/bin/env python3
"""
Setup script for historical OCR resources.

This script configures Tesseract for optimal performance on historical documents
by setting up custom dictionaries and patterns for improved recognition.
"""

import os
import shutil
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

def setup_historical_resources(tessdata_prefix=None):
    """Configure Tesseract with historical resources.
    
    Args:
        tessdata_prefix: Custom tessdata directory. If None, uses environment variable
                        or default location.
    """
    
    logger.info("Setting up historical OCR resources...")
    
    # Determine Tesseract data directory
    if tessdata_prefix is None:
        tessdata_prefix = os.environ.get('TESSDATA_PREFIX', '/usr/share/tesseract-ocr/5/tessdata')
    tessdata_dir = Path(tessdata_prefix)
    
    # Ensure required directories exist
    configs_dir = tessdata_dir / 'configs'
    historical_words_dir = tessdata_dir / 'historical_words'
    
    configs_dir.mkdir(exist_ok=True)
    historical_words_dir.mkdir(exist_ok=True)
    
    logger.info(f"Using Tesseract data directory: {tessdata_dir}")
    
    # Get current script directory
    script_dir = Path(__file__).parent.absolute()
    words_dir = script_dir / 'words'
    
    # Copy historical word lists from package directory
    word_files = [
        'historical_pre1800.txt',
        'historical_19thC.txt',
        'historical_early20thC.txt',
        'historical_patterns.txt'
    ]
    
    for file in word_files:
        source = words_dir / file
        target = historical_words_dir / file
        
        if source.exists():
            shutil.copy2(source, target)
            logger.info(f"Copied {file} to {target}")
        else:
            logger.warning(f"Source file not found: {source}")
    
    # Create Tesseract config files for historical documents
    create_historical_config_files(configs_dir, historical_words_dir)
    
    logger.info("Historical OCR resource setup complete")

def create_historical_config_files(configs_dir, historical_words_dir):
    """Create Tesseract configuration files for historical documents."""
    
    # Configuration for pre-1800 documents
    pre1800_config = f"""
# Configuration for pre-1800 historical documents
tessedit_char_whitelist abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:!?()[]{{}}'"-—–/&%$#@*+=_\\
load_system_dawg 1
load_freq_dawg 1
user_words_suffix historical_words/historical_pre1800.txt
tessedit_pageseg_mode 1
textord_heavy_nr 1
textord_noise_rejwords 1
textord_noise_rejrows 1
textord_noise_debug_images 0
textord_noise_sizelimit 0.5
textord_noise_normratio 8
textord_noise_snr 1
tessedit_preserve_interword_spaces 1
language_model_ngram_on 1
tessedit_pageseg_mode 1
thresholding_debug 0
textord_heavy_nr 1
textord_noise_rejwords 1
textord_noise_rejrows 1
classify_bln_numeric_mode 1
preserve_interword_spaces 1
tessedit_enable_doc_dict 1
user_patterns_suffix historical_words/historical_patterns.txt
"""
    
    # Configuration for 19th century documents
    nineteenth_config = f"""
# Configuration for 19th century documents
tessedit_char_whitelist abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:!?()[]{{}}'"-—–/&%$#@*+=_\\
load_system_dawg 1
load_freq_dawg 1
user_words_suffix historical_words/historical_19thC.txt
tessedit_pageseg_mode 1
textord_noise_rejwords 1
textord_noise_rejrows 1
tessedit_preserve_interword_spaces 1
language_model_ngram_on 1
textord_heavy_nr 1
tessedit_pageseg_mode 1
thresholding_debug 0
thresholding_method 1
classify_bln_numeric_mode 1
preserve_interword_spaces 1
tessedit_enable_doc_dict 1
user_patterns_suffix historical_words/historical_patterns.txt
"""
    
    # Configuration for early 20th century documents
    early20th_config = f"""
# Configuration for early 20th century documents
tessedit_char_whitelist abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:!?()[]{{}}'"-—–/&%$#@*+=_\\
load_system_dawg 1
load_freq_dawg 1
user_words_suffix historical_words/historical_early20thC.txt
tessedit_pageseg_mode 1
tessedit_preserve_interword_spaces 1
language_model_ngram_on 1
tessedit_enable_doc_dict 1
user_patterns_suffix historical_words/historical_patterns.txt
"""
    
    # Generic historical document configuration
    historical_general_config = f"""
# Configuration for general historical documents
tessedit_char_whitelist abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:!?()[]{{}}'"-—–/&%$#@*+=_\\
load_system_dawg 1
load_freq_dawg 1
tessedit_pageseg_mode 1
textord_tabfind_find_tables 1
textord_tablefind_recognize_tables 1
textord_min_linesize 1.25
textord_noise_sizelimit 0.5
textord_noise_normratio 6
tessedit_preserve_interword_spaces 1
language_model_ngram_on 1
textord_heavy_nr 1
thresholding_debug 0
thresholding_method 1
textord_noise_debug_images 0
classify_bln_numeric_mode 1
preserve_interword_spaces 1
tessedit_enable_doc_dict 1
user_patterns_suffix historical_words/historical_patterns.txt
"""
    
    configs = {
        'historical_pre1800.txt': pre1800_config.strip(),
        'historical_19thC.txt': nineteenth_config.strip(),
        'historical_early20thC.txt': early20th_config.strip(),
        'historical_general.txt': historical_general_config.strip(),
    }
    
    for filename, content in configs.items():
        config_file = configs_dir / filename
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Created config file: {config_file}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    setup_historical_resources()