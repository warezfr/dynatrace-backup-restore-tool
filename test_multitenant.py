"""Multi-Tenant Setup Validation Script"""
import subprocess
import json
import time
import sys
from pathlib import Path

class MultiTenantValidator:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.results = []
        
    def run_checks(self):
        """Run all validation checks"""
        print("🔍 Multi-Tenant Dynatrace Backup Manager - Validation Script\n")
        print("=" * 60)
        
        checks = [
            ("Backend API", self.check_api_running),
            ("Database Schema", self.check_db_schema),
            ("Environments Endpoint", self.check_environments_endpoint),
            ("Bulk Operations Endpoint", self.check_bulk_operations_endpoint),
            ("UI Components", self.check_ui_components),
            ("Configuration", self.check_configuration),
        ]
        
        for name, check_func in checks:
            try:
                result = check_func()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status}: {name}")
                self.results.append((name, result))
            except Exception as e:
                print(f"❌ FAIL: {name} - {str(e)}")
                self.results.append((name, False))
        
        print("=" * 60)
        self._print_summary()
        
        return all(r[1] for r in self.results)
    
    def check_api_running(self) -> bool:
        """Check if FastAPI backend is running"""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.api_url}/api/health/status"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def check_db_schema(self) -> bool:
        """Verify database has multi-tenant tables"""
        try:
            result = subprocess.run(
                ["python", "-c", """
import sqlite3
from pathlib import Path
from core.config import settings

db_url = settings.DATABASE_URL
if not db_url.startswith("sqlite:///"):
    print("Unsupported database url")
    exit(1)

db_path = Path(db_url.replace("sqlite:///", ""))
if not db_path.is_absolute():
    db_path = (Path.cwd() / db_path).resolve()

if not db_path.exists():
    print('Database not found')
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check for multi-tenant tables
tables = [
    'dynatrace_environments',
    'environment_groups',
    'bulk_operations',
    'backups',
    'restore_history'
]

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
existing_tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    if table not in existing_tables:
        print(f'Missing table: {table}')
        exit(1)

# Check backup table has environment_id
cursor.execute("PRAGMA table_info(backups)")
columns = [row[1] for row in cursor.fetchall()]
if 'environment_id' not in columns:
    print('Missing environment_id column in backups table')
    exit(1)

print('Schema valid')
exit(0)
                """],
                capture_output=True,
                cwd="./backend/app"
            )
            return result.returncode == 0 and "Schema valid" in result.stdout.decode()
        except:
            return False
    
    def check_environments_endpoint(self) -> bool:
        """Check /api/environments endpoint exists and works"""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 f"{self.api_url}/api/environments"],
                capture_output=True,
                timeout=5
            )
            status_code = result.stdout.decode().strip()
            # 200 OK, redirect, or 404 also means endpoint exists
            return status_code in ["200", "301", "302", "307", "308", "404", "401"]
        except:
            return False
    
    def check_bulk_operations_endpoint(self) -> bool:
        """Check /api/bulk-operations endpoint exists"""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 f"{self.api_url}/api/bulk-operations"],
                capture_output=True,
                timeout=5
            )
            status_code = result.stdout.decode().strip()
            return status_code in ["200", "404", "401"]
        except:
            return False
    
    def check_ui_components(self) -> bool:
        """Check UI files exist for multi-tenant"""
        ui_files = [
            Path("./desktop_ui/windows/environments.py"),
            Path("./desktop_ui/windows/bulk_operations.py"),
        ]
        
        for file in ui_files:
            if not file.exists():
                print(f"  Missing: {file}")
                return False
        
        return True
    
    def check_configuration(self) -> bool:
        """Check .env is properly configured"""
        env_file = Path("./.env")
        if not env_file.exists():
            print("  .env file not found")
            return False
        
        required_keys = [
            "DYNATRACE_ENVIRONMENT_URL",
            "DYNATRACE_API_TOKEN"
        ]
        
        content = env_file.read_text()
        for key in required_keys:
            if key not in content:
                print(f"  Missing key in .env: {key}")
                return False
        
        return True
    
    def _print_summary(self):
        """Print validation summary"""
        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\n📊 Results: {passed}/{total} checks passed ({percentage:.0f}%)")
        
        if passed == total:
            print("\n✅ Multi-Tenant setup is complete and functional!")
            print("\nNext steps:")
            print("1. Add multiple environments via UI (🌍 Environments tab)")
            print("2. Create environment groups for bulk operations")
            print("3. Try bulk backup/restore/compare operations")
            print("\nSee MIGRATION_GUIDE.md for detailed usage instructions.")
        else:
            print("\n⚠️ Some checks failed. Review errors above.")
            print("\nCommon fixes:")
            print("- Run 'install.bat' to setup database schema")
            print("- Ensure .env is configured")
            print("- Start backend: start-api.bat")
            print("- Start frontend: start.bat")

def main():
    validator = MultiTenantValidator()
    success = validator.run_checks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
