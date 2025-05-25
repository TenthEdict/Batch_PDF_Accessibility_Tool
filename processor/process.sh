#!/bin/bash
# Activate virtual environment
source ../venv/bin/activate

# Run with lower thread count and force terminal output flushing
python -u process_academic_local.py --batch --max-workers 4 /home/schipp0/ePubs_Main/data/input /home/schipp0/ePubs_Main/data/output
