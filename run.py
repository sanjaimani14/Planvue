import sys
from pathlib import Path
import uvicorn

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

def main():
    print("=" * 60)
    print("  PLANE VUE — AI Spatial Reconstruction Backend")
    print("  Mode A Core Pipeline & Foundation Active")
    print("  Listening on: http://127.0.0.1:8000")
    print("  Health check: http://127.0.0.1:8000/api/health")
    print("=" * 60)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
