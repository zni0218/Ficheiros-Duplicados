"""
indexing/tlsh_hash.py

✅ geração de hash TLSH
"""

from pathlib import Path
import time

try:
    import tlsh
except Exception as e:
    tlsh = None
    TLSH_ERROR = str(e)


# ============================================================
# DEBUG
# ============================================================

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# ============================================================
# INDEXAÇÃO
# ============================================================

def compute_index_tlsh(files: list[Path], debug=False):

    if tlsh is None:
        raise RuntimeError(f"TLSH indisponível: {TLSH_ERROR}")

    index = []

    for fp in files:

        start = time.perf_counter()

        try:
            data = fp.read_bytes()

            # ✅ filtro mínimo de tamanho (evita quase todos TNULL)
            if len(data) < 512:
                continue

            h = tlsh.hash(data)
                        
            if debug and (not h or h == "TNULL"):
                print(f"[DEBUG] TLSH ignorado (inválido): {fp}")

            # ✅ IGNORAR TNULL (CRÍTICO)
            if not h or h == "TNULL":
                continue

        except Exception:
            continue

        elapsed = max(0.000001, round((time.perf_counter() - start) * 1000, 6))

        index.append({
            "file_path": fp,
            "method": "tlsh",
            "fingerprint": h,
            "execution_time_ms": elapsed,
        })

    return index