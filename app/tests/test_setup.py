"""
Test to verify project setup is working correctly
"""

import os
import sys

def test_project_structure():
    """Test that all required directories and files exist"""

    # Test directories
    required_dirs = [
        'app',
        'app/api',
        'app/core',
        'app/models',
        'app/services',
        'app/tools',
        'app/rag',
        'app/tests',
        'data'
    ]

    for dir_path in required_dirs:
        assert os.path.exists(dir_path), f"Directory {dir_path} does not exist"

    # Test key files
    required_files = [
        'app/main.py',
        'app/core/config.py',
        'app/api/chat.py',
        'app/models/chat.py',
        'requirements.txt',
        'run.py'
    ]

    for file_path in required_files:
        assert os.path.exists(file_path), f"File {file_path} does not exist"

    print("✓ All project structure tests passed!")

def test_requirements():
    """Test that requirements can be imported"""
    try:
        import fastapi
        import pydantic
        import pandas
        print("✓ All dependencies can be imported successfully!")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        raise

if __name__ == "__main__":
    test_project_structure()
    test_requirements()
    print("All setup tests passed! Project structure is ready.")