"""One-click setup and execution script for the premium AI Resume Screening Dashboard.
"""

import os
import sys
import subprocess

def log(msg):
    print(f"\n[INFO] {msg}")

def error(msg):
    print(f"\n[ERROR] {msg}")

def main():
    log("Initializing Premium AI Resume Screening Engine...")
    
    # 1. Detect virtual environment
    venv_dir = os.path.join(os.path.dirname(__file__), ".venv")
    if not os.path.exists(venv_dir):
        log("Creating Python virtual environment (.venv)...")
        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        except Exception as e:
            error(f"Failed to create virtual environment: {str(e)}")
            sys.exit(1)
            
    # Choose python/pip executables
    if sys.platform == "win32":
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        python_exe = os.path.join(venv_dir, "bin", "python")
        pip_exe = os.path.join(venv_dir, "bin", "pip")

    # 2. Verify dependencies are installed
    requirements_txt = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_txt):
        log("Updating/installing package dependencies from requirements.txt...")
        try:
            subprocess.run([pip_exe, "install", "-r", requirements_txt], check=True)
        except Exception as e:
            error(f"Failed to install python packages: {str(e)}")
            sys.exit(1)
            
    # 3. Startup the Uvicorn FastAPI Server hosting both API endpoints and the dashboard UI
    log("Launching FastAPI Application Server...")
    log("Dashboard will be available at: http://localhost:8000")
    
    try:
        # Run uvicorn server (relative import paths must match backend.main:app)
        subprocess.run([
            python_exe, "-m", "uvicorn", "backend.main:app", 
            "--host", "127.0.0.1", "--port", "8000", "--reload"
        ])
    except KeyboardInterrupt:
        log("Server stopped by user. Goodbye!")
    except Exception as e:
        error(f"Failed to start Uvicorn server: {str(e)}")

if __name__ == "__main__":
    main()
