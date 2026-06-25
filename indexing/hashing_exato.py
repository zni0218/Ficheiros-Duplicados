"""
hashing_exato.py

Geração de hash exato com SHA-256

- identifica duplicados exatos
- usado como método base no index
"""

from pathlib import Path
import time

from utils.file_utils import sha256_file


# DEBUG

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# INDEXAÇÃO

def compute_index_hashing_exato(files: list[Path], debug: bool = False):
    """
    Gera hashes SHA-256 para ficheiros.
    """

    debug_print(debug, "Index SHA-256")

    index = []

    for fp in files:

        start = time.perf_counter()

        try:
            # calcular hash
            digest = sha256_file(fp)

        except Exception:
            # ignorar ficheiros problemáticos
            continue

        # tempo por ficheiro (ms)
        elapsed = max(
            0.000001,
            round((time.perf_counter() - start) * 1000, 6)
        )

        index.append({
            "file_path": fp,
            "method": "hashing_exato",
            "fingerprint": digest,
            "execution_time_ms": elapsed,
        })

    return index
