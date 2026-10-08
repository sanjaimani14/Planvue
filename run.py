"""
PLANE VUE — Unified Application Launcher (Section 4)
Orchestrates dependency check, directory structure verification, port conflict check,
and starts the local backend server with clean URL reporting.
"""
import sys
import os
import socket
import subprocess
import time
import signal
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

REQUIRED_DIRS = [
    BASE_DIR / "data" / "uploads",
    BASE_DIR / "data" / "processed",
    BASE_DIR / "data" / "demo",
    BASE_DIR / "outputs" / "scenes",
    BASE_DIR / "outputs" / "reports",
    BASE_DIR / "outputs" / "exports",
    BASE_DIR / "outputs" / "geometry"
]

def check_port(host: str, port: int) -> bool:
    """Returns True if port is in use / busy."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def ensure_directories():
    for d in REQUIRED_DIRS:
        d.mkdir(parents=True, exist_ok=True)

def verify_core_dependencies():
    missing = []
    for pkg in ["fastapi", "uvicorn", "numpy", "cv2", "PIL", "trimesh", "shapely"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[ERROR] Missing required Python packages: {missing}")
        print("Please run: pip install -r requirements.txt")
        return False
    return True

def main():
    print("=" * 65)
    print("  PLANE VUE — AI Spatial Reconstruction Platform")
    print("  'See the space. Reconstruct the unseen.'")
    print("=" * 65)

    # 1. Dependency verification
    if not verify_core_dependencies():
        sys.exit(1)

    # 2. Directory structure verification
    ensure_directories()
    print("[OK] Workspace directories verified.")

    # 3. Port check
    backend_port = 8000
    if check_port("127.0.0.1", backend_port):
        print(f"[NOTE] Port {backend_port} is already active (server might be running).")
    else:
        print(f"[OK] Port {backend_port} available for FastAPI backend.")

    frontend_port = 5173
    fe_active = check_port("127.0.0.1", frontend_port)
    if fe_active:
        print(f"[OK] Frontend active on: http://127.0.0.1:{frontend_port}")
    else:
        print(f"[INFO] Frontend dev server not detected on {frontend_port}.")
        print("       To start frontend: cd frontend && npm run dev")

    print("\n" + "-" * 65)
    print("  APPLICATION ACCESS URLS:")
    print("  • Frontend UI:     http://127.0.0.1:5173")
    print("  • Backend API:     http://127.0.0.1:8000")
    print("  • API Docs:        http://127.0.0.1:8000/docs")
    print("  • Health Check:    http://127.0.0.1:8000/api/health")
    print("  • Mode:            Local Offline-First (No external keys needed)")
    print("-" * 65)
    print("Starting FastAPI backend server (Press Ctrl+C to stop)...")
    print("=" * 65 + "\n")

    import uvicorn
    try:
        uvicorn.run("backend.app.main:app", host="127.0.0.1", port=backend_port, reload=False)
    except KeyboardInterrupt:
        print("\n[STOP] Shutting down PLANE VUE backend cleanly.")

if __name__ == "__main__":
    main()
