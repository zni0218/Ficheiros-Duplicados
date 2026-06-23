"""
indexing/hashing_exato.py

✅ geração de hash SHA-256
✅ usado no build_index
"""

from pathlib import Path
import time

from utils.file_utils import sha256_file


# ============================================================
# DEBUG
# ============================================================

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# ============================================================
# INDEXAÇÃO
# ============================================================

def compute_index_hashing_exato(files: list[Path], debug: bool = False):

    debug_print(debug, "Index SHA-256")

    index = []

    for fp in files:

        start = time.perf_counter()

        try:
            digest = sha256_file(fp)
        except Exception:
            continue  # ✅ temp-friendly

        elapsed = max(0.000001, round((time.perf_counter() - start) * 1000, 6))

        index.append({
            "file_path": fp,
            "method": "hashing_exato",
            "fingerprint": digest,
            "execution_time_ms": elapsed,
        })

    return index
