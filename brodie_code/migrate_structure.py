#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import re

def ensure_dir(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)

def remove_dir_if_empty(path):
    """Remove directory if it's empty."""
    try:
        path = Path(path)
        if path.exists() and path.is_dir():
            if not any(path.iterdir()):
                path.rmdir()
                print(f"Removed empty directory: {path}")
    except Exception as e:
        print(f"Warning: Could not remove directory {path}: {e}")

def migrate_directory_structure(project_root):
    """Migrate the project directory structure."""
    project_root = Path(project_root)
    
    print("\n1. Setting up correct directories...")
    # Ensure top-level directories exist
    ensure_dir(project_root / "input")
    ensure_dir(project_root / "output")
    
    # Create new build directory
    src_path = project_root / "src" / "accessibility_checker"
    ensure_dir(src_path / "build")
    
    print("\n2. Moving build process file...")
    # Move build process file
    old_process_path = src_path / "core" / "build" / "process.py"
    new_process_path = src_path / "build" / "process.py"
    
    if old_process_path.exists():
        # Create parent directory if it doesn't exist
        new_process_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file to new location
        shutil.copy2(old_process_path, new_process_path)
        print(f"Moved process.py to: {new_process_path}")
        
        # Remove old file and its parent directory if empty
        old_process_path.unlink()
        print(f"Removed old process.py from: {old_process_path}")
        
        # Try to remove empty build directory in core
        remove_dir_if_empty(old_process_path.parent)
    
    print("\n3. Cleaning up redundant directories...")
    # Remove redundant input/output directories in src
    redundant_dirs = [
        project_root / "src" / "input",
        project_root / "src" / "output"
    ]
    
    for dir_path in redundant_dirs:
        if dir_path.exists():
            # Move any contents to top-level directories
            if dir_path.name == "input":
                target_dir = project_root / "input"
            else:
                target_dir = project_root / "output"
                
            try:
                for item in dir_path.iterdir():
                    target_path = target_dir / item.name
                    if not target_path.exists():
                        if item.is_dir():
                            shutil.copytree(item, target_path)
                        else:
                            shutil.copy2(item, target_path)
                        print(f"Moved {item.name} to {target_dir}")
                
                # Remove the directory after moving contents
                shutil.rmtree(dir_path)
                print(f"Removed redundant directory: {dir_path}")
            except Exception as e:
                print(f"Warning: Could not fully process {dir_path}: {e}")
    
    print("\n4. Updating imports...")
    # Update imports in Python files
    for py_file in src_path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update import patterns
            new_content = re.sub(
                r'from [\w.]*core\.build\.process',
                'from ..build.process',
                content
            )
            
            if new_content != content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated imports in: {py_file}")
        except Exception as e:
            print(f"Warning: Could not process {py_file}: {e}")
    
    print("\nMigration completed!")
    print("\nPlease verify the following:")
    print("1. All files from src/input and src/output were moved correctly")
    print("2. The build process.py file is in the new location")
    print("3. No import statements are broken")
    print("4. The Docker container still works with the top-level input/output directories")

if __name__ == "__main__":
    # Get the project root (assuming this script is in the project root)
    project_root = Path.cwd()
    
    print(f"Project root: {project_root}")
    response = input("Proceed with migration? (y/N): ")
    
    if response.lower() == 'y':
        migrate_directory_structure(project_root)
    else:
        print("Migration cancelled.")
