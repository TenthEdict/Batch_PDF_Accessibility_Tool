#!/usr/bin/env python3
import os
from pathlib import Path
import re

def fix_output_paths(project_root):
    """Fix output paths in code analyzer files."""
    project_root = Path(project_root)
    
    # Files to check
    files_to_update = [
        project_root / "src" / "accessibility_checker" / "utils" / "code_analyzer.py",
        project_root / "src" / "accessibility_checker" / "build" / "process.py",
        project_root / "src" / "main.py"
    ]
    
    print("\nUpdating output paths in files...")
    
    for file_path in files_to_update:
        if not file_path.exists():
            print(f"Warning: File not found: {file_path}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update paths
            new_content = content.replace(
                'project_root / "src" / "output"',
                'project_root / "output"'
            )
            new_content = new_content.replace(
                '"src/output"',
                '"output"'
            )
            new_content = new_content.replace(
                '/app/src/output',
                '/app/output'
            )
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated paths in: {file_path}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Move any existing analysis files
    src_analysis_dir = project_root / "src" / "output" / "analysis"
    dest_analysis_dir = project_root / "output" / "analysis"
    
    if src_analysis_dir.exists():
        print("\nMoving existing analysis files...")
        dest_analysis_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            for file in src_analysis_dir.glob("*.json"):
                dest_file = dest_analysis_dir / file.name
                if not dest_file.exists():
                    file.rename(dest_file)
                    print(f"Moved: {file.name}")
        except Exception as e:
            print(f"Error moving analysis files: {e}")
    
    # Clean up any empty src/output directory
    try:
        src_output = project_root / "src" / "output"
        if src_output.exists():
            if not any(src_output.iterdir()):
                src_output.rmdir()
                print("\nRemoved empty src/output directory")
            else:
                print("\nWarning: src/output directory still contains files")
    except Exception as e:
        print(f"Error cleaning up src/output: {e}")

    print("\nOutput path fixes completed!")
    print("Please verify:")
    print("1. All analysis files are now in /output/analysis")
    print("2. Docker container writes to correct location")
    print("3. No code analyzer tests are broken")

if __name__ == "__main__":
    project_root = Path.cwd()
    print(f"Project root: {project_root}")
    response = input("Proceed with fixing output paths? (y/N): ")
    
    if response.lower() == 'y':
        fix_output_paths(project_root)
    else:
        print("Operation cancelled.")
