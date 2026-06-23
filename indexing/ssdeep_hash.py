"""
indexing/ssdeep_hash.py

✅ geração de assinatura ssdeep
"""

from pathlib import Path
import time

try:
    import ssdeep
    _ = ssdeep.hash(b"test")
except Exception as e:
    ssdeep = None
    SSDEEP_ERROR = str(e)


# ============================================================
# DEBUG
# ============================================================

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# ============================================================
# INDEXAÇÃO
# ============================================================

def compute_index_ssdeep(files: list[Path], debug=False):

    if ssdeep is None:
        raise RuntimeError(f"ssdeep indisponível: {SSDEEP_ERROR}")

    index = []

    for fp in files:

        start = time.perf_counter()

        try:
            with open(fp, "rb") as f:
                fingerprint = ssdeep.hash(f.read())
        except Exception:
            continue

        elapsed = max(0.000001, round((time.perf_counter() - start) * 1000, 6))

        index.append({
            "file_path": fp,
            "method": "ssdeep",
            "fingerprint": fingerprint,
            "execution_time_ms": elapsed,
        })

    return index
