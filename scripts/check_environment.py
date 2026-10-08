"""
PLANE VUE — Environment & Dependency Check (Section 5)
Checks Python version, Node.js, npm, core libraries, and optional reconstruction packages.
"""
import sys
import subprocess
import shutil
from pathlib import Path

REQUIRED_PYTHON_PACKAGES = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("numpy", "NumPy"),
    ("cv2", "OpenCV (opencv-python)"),
    ("PIL", "Pillow"),
    ("scipy", "SciPy"),
    ("shapely", "Shapely"),
    ("trimesh", "Trimesh"),
    ("pydantic", "Pydantic")
]

OPTIONAL_PACKAGES = [
    ("pycolmap", "PyCOLMAP (Heavy SfM - optional)"),
    ("open3d", "Open3D (Point cloud processing - optional)"),
    ("torch", "PyTorch (Deep learning - optional)")
]

def check_command(cmd):
    try:
        out = subprocess.check_output(f"{cmd} --version", shell=True, stderr=subprocess.STDOUT, text=True, timeout=3).strip()
        return out.split('\n')[0]
    except Exception:
        path = shutil.which(cmd)
        return "Available" if path else None

def check_environment():
    print("=" * 65)
    print("  PLANE VUE — SYSTEM ENVIRONMENT CHECK")
    print("=" * 65)

    all_passed = True

    # 1. Python Version
    py_ver = sys.version.split()[0]
    py_major, py_minor = sys.version_info.major, sys.version_info.minor
    py_ok = (py_major == 3 and py_minor >= 10)
    print(f"Python Version:       {py_ver:<15} [{'PASS' if py_ok else 'FAIL'}] (Requires Python >= 3.10)")
    if not py_ok:
        all_passed = False

    # 2. Node & NPM
    node_ver = check_command("node")
    npm_ver = check_command("npm")
    print(f"Node.js Runtime:      {str(node_ver):<15} [{'PASS' if node_ver else 'WARNING'}]")
    print(f"NPM Package Manager:  {str(npm_ver):<15} [{'PASS' if npm_ver else 'WARNING'}]")

    # 3. Required Python Packages
    print("\n--- Required Core Python Libraries ---")
    for mod_name, label in REQUIRED_PYTHON_PACKAGES:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "Installed")
            print(f"  {label:<25} {ver:<15} [AVAILABLE]")
        except ImportError:
            print(f"  {label:<25} {'Missing':<15} [NOT INSTALLED - REQUIRED]")
            all_passed = False

    # 4. Optional Packages
    print("\n--- Optional Acceleration Libraries ---")
    for mod_name, label in OPTIONAL_PACKAGES:
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "Installed")
            print(f"  {label:<25} {ver:<15} [AVAILABLE]")
        except ImportError:
            print(f"  {label:<25} {'Not installed':<15} [OPTIONAL]")

    # 5. Frontend Dependencies Check
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    node_modules = frontend_dir / "node_modules"
    has_nm = node_modules.exists()
    print("\n--- Frontend Build Dependencies ---")
    print(f"  frontend/node_modules   {'Present' if has_nm else 'Missing':<15} [{'PASS' if has_nm else 'WARNING'}]")
    if not has_nm:
        print("  --> Run 'npm install' inside the frontend directory.")

    print("\n" + "=" * 65)
    if all_passed:
        print("ENVIRONMENT STATUS: READY FOR PLANE VUE EXECUTION")
    else:
        print("ENVIRONMENT STATUS: MISSING REQUIRED DEPENDENCIES")
    print("=" * 65)

    return all_passed

if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)
