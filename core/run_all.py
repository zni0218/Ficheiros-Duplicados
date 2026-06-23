"""
run_all.py (FINAL REFACTORED)

✅ pipeline:
    validation → build_index → run_detection

✅ mede:
    - tempo por método
    - tempo por ficheiro (end-to-end)

✅ outputs:
    - resultados CSV
    - performance por método CSV
    - performance por ficheiro CSV
"""

import argparse
import csv
import time
from pathlib import Path

from utils.path_utils_safe import safe_path
from utils.path_utils import path_for_csv

from core.run_validation import run_validation
from core.build_index import build_index
from core.run_detection import run_detection


# ============================================================
# CSV HELPERS
# ============================================================

def write_csv(path: Path, rows: list[dict]):

    if not rows:
        return

    with open(safe_path(path), "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# MAIN
# ============================================================

def run_all(base: Path, out: Path, debug=False):

    base = Path(safe_path(base))
    out = Path(safe_path(out))

    out.mkdir(parents=True, exist_ok=True)

    idx_dir = out / "dataset_index"
    res_dir = out / "results"
    perf_dir = out / "performance"

    for d in [idx_dir, res_dir, perf_dir]:
        d.mkdir(exist_ok=True)

    # ========================================================
    # GLOBAL TIMER
    # ========================================================

    pipeline_start = time.perf_counter()

    # ========================================================
    # FILE TIMERS
    # ========================================================

    file_times = {}  # path → total time

    # ========================================================
    # 1) VALIDATION
    # ========================================================

    t0 = time.perf_counter()

    validation = run_validation(
        base=base,
        out=out / "validation",
        debug=debug,
        temp_mode=False
    )

    valid_files = validation["valid_files"]

    t_validation = time.perf_counter() - t0

    # inicializar tempos por ficheiro
    for f in valid_files:
        file_times[str(f)] = t_validation / max(len(valid_files), 1)

    if not valid_files:
        print("[ERROR] Nenhum ficheiro válido")
        return

    # ========================================================
    # 2) BUILD INDEX
    # ========================================================

    t0 = time.perf_counter()

    build_index(
        base=base,
        out=out,
        debug=debug,
        temp_mode=False
    )

    t_index = time.perf_counter() - t0

    for f in valid_files:
        file_times[str(f)] += t_index / len(valid_files)

    # ========================================================
    # 3) DETECTION
    # ========================================================

    t0 = time.perf_counter()

    results = run_detection(
        index_dir=out / "dataset_index",
        temp_dir=None,
        debug=debug
    )

    t_detection = time.perf_counter() - t0

    # distribuir custo por ficheiro
    for f in valid_files:
        file_times[str(f)] += t_detection / len(valid_files)

    # ========================================================
    # 4) ORGANIZAR RESULTADOS
    # ========================================================

    per_method = {}
    exact_rows = []
    near_rows = []

    for r in results:

        method = r["method"]

        row = {
            "method": method,
            "path_1": r["file_a"],
            "path_2": r["file_b"],
            "raw_score": r["raw_score"],
            "normalized_score": r["normalized_score"],
            "is_exact_duplicate": r["is_exact_duplicate"],
            "is_near_duplicate": r["is_near_duplicate"],
            "execution_time_ms": r["execution_time_ms"],
        }

        per_method.setdefault(method, []).append(row)

        if r["is_exact_duplicate"]:
            exact_rows.append(row)
        else:
            near_rows.append(row)

    # ========================================================
    # 5) WRITE RESULTADOS
    # ========================================================

    for method, rows in per_method.items():
        write_csv(res_dir / f"{method}.csv", rows)

    write_csv(res_dir / "ALL_exact.csv", exact_rows)
    write_csv(res_dir / "ALL_near.csv", near_rows)
    write_csv(res_dir / "ALL_combined.csv", results)

    # ========================================================
    # 6) PERFORMANCE POR MÉTODO
    # ========================================================

    method_perf = []

    method_times = {}

    for r in results:
        method = r["method"]
        method_times.setdefault(method, 0)
        method_times[method] += r["execution_time_ms"]

    for method, t in method_times.items():
        method_perf.append({
            "method": method,
            "total_execution_time_ms": round(t, 4)
        })

    write_csv(perf_dir / "performance_methods.csv", method_perf)

    # ========================================================
    # 7) PERFORMANCE POR FICHEIRO
    # ========================================================

    file_perf = []

    for path, t in file_times.items():
        file_perf.append({
            "file": path,
            "total_pipeline_time_s": round(t, 4)
        })

    write_csv(perf_dir / "performance_files.csv", file_perf)

    # ========================================================
    # 8) GLOBAL
    # ========================================================

    total_time = time.perf_counter() - pipeline_start

    write_csv(perf_dir / "performance_global.csv", [{
        "total_pipeline_time_s": round(total_time, 4),
        "validation_s": round(t_validation, 4),
        "index_s": round(t_index, 4),
        "detection_s": round(t_detection, 4),
        "total_files": len(valid_files)
    }])

    print(f"[OK] Pipeline completo em {total_time:.4f}s")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser()

    parser.add_argument("--base", default=str(PROJECT_ROOT / "data/original_files"))
    parser.add_argument("--out", default=str(PROJECT_ROOT / "data/outputs/run_all"))
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    run_all(
        base=Path(args.base),
        out=Path(args.out),
        debug=args.debug
    )
