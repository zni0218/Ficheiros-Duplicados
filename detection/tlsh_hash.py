"""
tlsh_hash.py

Comparação fuzzy com TLSH

- funciona em todas as categorias
- compara apenas dentro da mesma categoria
- gera resultados completos (positivos e negativos)
"""

from itertools import combinations
import time
from pathlib import Path

# tentativa de import (pode falhar)
try:
    import tlsh
except Exception:
    tlsh = None

from utils.score_utils import classify_score
from utils.file_utils import EXT_BY_CATEGORY


# CONFIG

# distância máxima esperada (referência)
MAX_DIST = 30


# MAP EXT → CATEGORY

EXT_TO_CATEGORY = {}

for cat, exts in EXT_BY_CATEGORY.items():
    for e in exts:
        EXT_TO_CATEGORY[e] = cat


def get_category(path: str):
    """
    Obtém categoria a partir da extensão.
    """
    ext = Path(path).suffix.lower()
    return EXT_TO_CATEGORY.get(ext, "unknown")


# MAIN

def compare_from_index(index_data: dict, debug=False):
    """
    Compara ficheiros usando TLSH.
    """

    # verificar disponibilidade
    if tlsh is None:
        return []

    results = []

    # agrupar por categoria
    category_map = {}

    for path, data in index_data.items():

        # ignorar hashes inválidos
        if not data.get("tlsh") or data.get("tlsh") == "TNULL":
            continue

        cat = get_category(path)

        category_map.setdefault(cat, []).append(path)

    # comparar dentro de cada categoria
    for cat, files in category_map.items():

        if len(files) < 2:
            continue

        if debug:
            print(f"[DEBUG] tlsh categoria {cat}: {len(files)} ficheiros")

        for f1, f2 in combinations(files, 2):

            start = time.perf_counter()

            try:
                # calcular distância TLSH
                raw_score = tlsh.diff(
                    index_data[f1]["tlsh"],
                    index_data[f2]["tlsh"]
                )

            except Exception:
                continue

            # tempo por comparação (ms)
            elapsed = max(
                0.000001,
                round((time.perf_counter() - start) * 1000, 6)
            )

            # ground truth (hash exato)
            sha_match = (
                index_data[f1].get("hashing_exato") ==
                index_data[f2].get("hashing_exato")
            )

            # classificação
            norm, is_exact, is_near, is_strong = classify_score(
                method="tlsh",
                raw_score=raw_score,
                sha_match=sha_match
            )

            results.append({
                "method": "tlsh",
                "file_a": f1,
                "file_b": f2,
                "raw_score": raw_score,
                "normalized_score": round(norm or 0.0, 4),
                "is_exact_duplicate": is_exact,
                "is_near_duplicate": is_near,
                "is_strong_near_duplicate": is_strong,
                "execution_time_ms": elapsed,
            })

    return results