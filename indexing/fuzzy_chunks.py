"""
indexing/fuzzy_chunks.py

✅ geração de fingerprints otimizada
✅ sampling início / meio / fim
✅ tamanho controlado (evita CSV gigante)
"""

from pathlib import Path
import time

from utils.file_utils import chunk_hashes


# ============================================================
# DEBUG
# ============================================================

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# ============================================================
# CONFIG
# ============================================================

MAX_CHUNKS = 100  # 🎯 valor ideal


# ============================================================
# SAMPLING INTELIGENTE
# ============================================================

def sample_chunks(chunks: list[str], max_chunks=MAX_CHUNKS):

    n = len(chunks)

    if n <= max_chunks:
        return chunks

    # distribuição
    n_start = max_chunks // 3
    n_end = max_chunks // 3
    n_mid = max_chunks - n_start - n_end

    # slices
    start = chunks[:n_start]

    mid_start = max(0, (n // 2) - (n_mid // 2))
    mid = chunks[mid_start: mid_start + n_mid]

    end = chunks[-n_end:]

    return start + mid + end


# ============================================================
# INDEXAÇÃO
# ============================================================

def compute_index_fuzzy_chunks(files: list[Path], debug=False):

    debug_print(debug, "Index fuzzy_chunks")

    index = []

    for fp in files:

        start_time = time.perf_counter()

        try:
            chunks = chunk_hashes(fp)

            # ✅ aplicar sampling
            chunks = sample_chunks(chunks)

        except Exception:
            continue

        elapsed = max(
            0.000001,
            round((time.perf_counter() - start_time) * 1000, 6)
        )

        # ✅ evita CSV gigante
        fp_repr = str(tuple(chunks))

        index.append({
            "file_path": fp,
            "method": "fuzzy_chunks",
            "fingerprint": fp_repr,
            "execution_time_ms": elapsed,
        })

        if debug:
            debug_print(debug, f"{fp} -> chunks usados: {len(chunks)}")

    return index