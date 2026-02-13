"""Simple test to verify installation and configuration"""
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("PyQt6", "PyQt6"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("requests", "Requests"),
        ("yaml", "PyYAML"),
    ]
    
    errors = []
    for package, name in packages:
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            errors.append(name)
    
    return len(errors) == 0

def test_project_structure():
    """Test if project structure is correct"""
    print("\nTesting project structure...")
    
    required_dirs = [
        "backend/app/api",
        "backend/app/models",
        "backend/app/services",
        "backend/app/core",
        "backend/app/database",
        "desktop_ui/windows",
        "backups",
    ]
    
    errors = []
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - MISSING")
            errors.append(dir_path)
    
    return len(errors) == 0

def test_configuration():
    """Test configuration files"""
    print("\nTesting configuration...")
    
    config_files = [
        ".env.example",
        "backend/app/core/config.py",
    ]
    
    errors = []
    for file_path in config_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            errors.append(file_path)
    
    # Check .env exists or create it
    if not Path(".env").exists():
        print("  ! .env not found, creating from .env.example...")
        try:
            import shutil
            shutil.copy(".env.example", ".env")
            print("  ✓ .env created")
        except:
            print("  ✗ Failed to create .env")
            errors.append(".env")
    else:
        print("  ✓ .env")
    
    return len(errors) == 0

def main():
    """Run all tests"""
    print("=" * 50)
    print("Dynatrace Backup Manager - Installation Test")
    print("=" * 50)
    print()
    
    results = {
        "Imports": test_imports(),
        "Project Structure": test_project_structure(),
        "Configuration": test_configuration(),
    }
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("✓ All tests passed! You're ready to go.")
        print()
        print("Next steps:")
        print("  1. Edit .env with your Dynatrace credentials")
        print("  2. Download Monaco CLI to bin/monaco.exe")
        print("  3. Run: start.bat (for GUI) or start-api.bat (for API)")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print()
        print("Try running: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
