"""
tlsh_hash.py

Geração de fingerprint TLSH

- fuzzy hashing baseado em distância
- robusto para ficheiros binários
"""

from pathlib import Path
import time

# tentativa de import (pode falhar)
try:
    import tlsh
except Exception as e:
    tlsh = None
    TLSH_ERROR = str(e)


# DEBUG

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# INDEXAÇÃO

def compute_index_tlsh(files: list[Path], debug=False):
    """
    Gera fingerprints TLSH para ficheiros.
    """

    # verificar disponibilidade
    if tlsh is None:
        raise RuntimeError(f"TLSH indisponível: {TLSH_ERROR}")

    index = []

    for fp in files:

        start = time.perf_counter()

        try:
            # ler ficheiro completo
            data = fp.read_bytes()

            # ignorar ficheiros muito pequenos
            if len(data) < 512:
                continue

            # calcular TLSH
            h = tlsh.hash(data)

            # debug opcional
            if debug and (not h or h == "TNULL"):
                print(f"[DEBUG] TLSH ignorado (inválido): {fp}")

            # ignorar resultados inválidos
            if not h or h == "TNULL":
                continue

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
            "method": "tlsh",
            "fingerprint": h,
            "execution_time_ms": elapsed,
        })

    return index