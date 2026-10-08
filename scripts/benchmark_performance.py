"""
PLANE VUE — Performance Benchmark & Hardware Audit (Sections 45 & 46)
Measures actual runtime latencies across multiple iterations:
- Blueprint processing
- Video reconstruction
- Unseen completion
- GLB binary export
Records machine hardware profile: CPU, RAM, OS, Python, Node versions.
"""
import sys
import os
import time
import statistics
import platform
import json
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_hardware_info():
    info = {
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "python_version": sys.version.split()[0],
    }
    # RAM and CPU count
    try:
        import psutil
        info["cpu_physical_cores"] = psutil.cpu_count(logical=False)
        info["cpu_logical_cores"] = psutil.cpu_count(logical=True)
        info["total_ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        info["cpu_cores"] = os.cpu_count()
        info["total_ram_gb"] = "Available"
    return info

def benchmark_pipeline():
    print("=" * 65)
    print("  PLANE VUE — PERFORMANCE BENCHMARK & HARDWARE PROFILE")
    print("=" * 65)

    hw = get_hardware_info()
    print("HARDWARE PROFILE:")
    for k, v in hw.items():
        print(f"  {k:<20}: {v}")
    print("-" * 65)

    # 1. Blueprint Processing (Mode A)
    blueprint_times = []
    print("Benchmarking Mode A Blueprint Processing (3 iterations)...")
    for i in range(3):
        t0 = time.time()
        res = client.post("/api/blueprint/reconstruct", data={"is_demo": "true", "demo_type": "simple"})
        assert res.status_code == 200
        blueprint_times.append((time.time() - t0) * 1000.0)

    # 2. Video Reconstruction & Completion (Mode B)
    video_times = []
    last_job_id = "sample_room_demo"
    print("Benchmarking Mode B Video Reconstruction & Completion (3 iterations)...")
    for i in range(3):
        t0 = time.time()
        res = client.post("/api/video/reconstruct", data={
            "video_id": "sample_room_demo",
            "target_keyframes": 6,
            "is_async": "false"
        })
        assert res.status_code == 200
        last_job_id = res.json().get("job_id", "sample_room_demo")
        video_times.append((time.time() - t0) * 1000.0)

    # 3. GLB Export
    export_times = []
    print("Benchmarking GLB Binary Export (3 iterations)...")
    for i in range(3):
        t0 = time.time()
        res = client.post(f"/api/video/completion/{last_job_id}/export", data={"format": "glb"})
        assert res.status_code == 200
        export_times.append((time.time() - t0) * 1000.0)

    def stats(arr):
        return {
            "mean_ms": round(statistics.mean(arr), 1),
            "median_ms": round(statistics.median(arr), 1),
            "min_ms": round(min(arr), 1),
            "max_ms": round(max(arr), 1),
            "samples": len(arr)
        }

    bench_results = {
        "hardware": hw,
        "mode_a_blueprint_reconstruction": stats(blueprint_times),
        "mode_b_video_reconstruction_completion": stats(video_times),
        "glb_binary_export": stats(export_times),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    print("\nBENCHMARK RESULTS (LATENCY IN MS):")
    for k in ["mode_a_blueprint_reconstruction", "mode_b_video_reconstruction_completion", "glb_binary_export"]:
        s = bench_results[k]
        print(f"  {k:<42}: Mean={s['mean_ms']}ms | Med={s['median_ms']}ms | Min={s['min_ms']}ms | Max={s['max_ms']}ms")

    print("=" * 65)

    # Save to outputs/reports/performance_benchmark.json
    out_dir = WORKSPACE_ROOT / "outputs" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "performance_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(bench_results, f, indent=2)

    return bench_results

if __name__ == "__main__":
    benchmark_pipeline()
