#!/usr/bin/env python3
"""
Test script for manual login functionality
"""
import sys
import os
sys.path.append('/home/schipp0/ePubs_Main')

from scraper.optimized_downloader import optimize_purdue_download
import tempfile

def test_manual_login():
    """Test the manual login functionality"""
    
    # Create temporary directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing manual login mode...")
        print(f"Download directory: {temp_dir}")
        print(f"=" * 60)
        
        # Test manual login
        try:
            success, failed = optimize_purdue_download(
                base_url="https://docs.lib.purdue.edu/roadschool/",
                download_dir=temp_dir,
                username=None,
                password=None,
                use_optimized_strategy=True,
                manual_login=True
            )
            
            print(f"Results: {success} successful, {failed} failed")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_manual_login()