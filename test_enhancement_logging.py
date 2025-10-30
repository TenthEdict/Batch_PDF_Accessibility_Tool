#!/usr/bin/env python3
"""Test enhancement service logging"""

import logging
import sys
from pathlib import Path

# Set up logging to see everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# Import after logging is configured
from processor.unified_project.src.services.enhancement_service import EnhancementService

print("="*70)
print("TESTING ENHANCEMENT SERVICE LOGGING")
print("="*70)

# Test input file
input_file = Path("/Users/broderickschipp/work/ePubs_Main/data/input/Ahmed et al. - 2025 - Using thematic analysis in qualitative research.pdf")
output_file = Path("/Users/broderickschipp/work/ePubs_Main/data/output/test_logging_output.pdf")

# Remove output if exists
if output_file.exists():
    output_file.unlink()

# Create service
print("\n1. Creating EnhancementService...")
service = EnhancementService()
print(f"   Service logger: {service.logger.name}")
print(f"   Service logger level: {service.logger.getEffectiveLevel()}")

# Call enhance_document
print("\n2. Calling enhance_document...")
print(f"   Input: {input_file.name}")
print(f"   Output: {output_file.name}")
print("\n" + "-"*70)
print("ENHANCEMENT SERVICE OUTPUT:")
print("-"*70 + "\n")

success = service.enhance_document(input_file, output_file)

print("\n" + "-"*70)
print(f"3. Result: {'SUCCESS' if success else 'FAILED'}")
print("="*70)
