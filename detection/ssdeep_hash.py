"""
ssdeep_hash.py

Comparação fuzzy com ssdeep

- funciona em todas as categorias
- compara apenas dentro da mesma categoria
- gera resultados completos (positivos e negativos)
"""

from itertools import combinations
import time
from pathlib import Path

# tentativa de import (pode falhar)
try:
    import ssdeep
except Exception:
    ssdeep = None

from utils.score_utils import classify_score
from utils.file_utils import EXT_BY_CATEGORY


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
    Compara ficheiros usando ssdeep.
    """

    # verificar disponibilidade
    if ssdeep is None:
        return []

    results = []

    # agrupar por categoria
    category_map = {}

    for path, data in index_data.items():

        # ignorar ficheiros sem fingerprint
        if not data.get("ssdeep"):
            continue

        cat = get_category(path)

        category_map.setdefault(cat, []).append(path)

    # comparar dentro de cada categoria
    for cat, files in category_map.items():

        if len(files) < 2:
            continue

        if debug:
            print(f"[DEBUG] ssdeep categoria {cat}: {len(files)}")

        for f1, f2 in combinations(files, 2):

            start = time.perf_counter()

            try:
                # calcular similaridade
                raw_score = ssdeep.compare(
                    index_data[f1]["ssdeep"],
                    index_data[f2]["ssdeep"]
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
                method="ssdeep",
                raw_score=raw_score,
                sha_match=sha_match
            )

            results.append({
                "method": "ssdeep",
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