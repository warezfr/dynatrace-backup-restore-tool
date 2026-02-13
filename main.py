"""Entry point for the entire application"""
import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Dynatrace Backup Manager for Managed Environments"
    )
    parser.add_argument(
        "--mode",
        choices=["gui", "api", "both"],
        default="both",
        help="Run mode: GUI only, API only, or both"
    )
    parser.add_argument(
        "--api-host",
        default="127.0.0.1",
        help="API host"
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=8000,
        help="API port"
    )
    
    args = parser.parse_args()
    
    if args.mode in ["api", "both"]:
        print("Starting FastAPI backend...")
        # TODO: Start API in separate thread
    
    if args.mode in ["gui", "both"]:
        print("Starting PyQt6 GUI...")
        from desktop_ui.main import main as gui_main
        gui_main()

if __name__ == "__main__":
    main()
