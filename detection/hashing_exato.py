"""
hashing_exato.py

Comparação baseada em hash exato (SHA-256)

- deteta duplicados perfeitos
- compara apenas dentro da mesma categoria
- evita comparações desnecessárias
"""

from itertools import combinations
import time
from pathlib import Path

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
    Compara ficheiros usando hashing exato.
    """

    results = []

    # agrupar ficheiros por categoria
    category_map = {}

    for path, data in index_data.items():

        # ignorar ficheiros sem hash
        if not data.get("hashing_exato"):
            continue

        cat = get_category(path)

        category_map.setdefault(cat, []).append(path)

    # comparar apenas dentro de cada categoria
    for cat, files in category_map.items():

        if len(files) < 2:
            continue

        if debug:
            print(f"[DEBUG] categoria {cat} -> {len(files)} ficheiros")

        for f1, f2 in combinations(files, 2):

            start = time.perf_counter()

            h1 = index_data[f1].get("hashing_exato")
            h2 = index_data[f2].get("hashing_exato")

            # duplicado exato
            is_dup = (h1 == h2)

            # tempo por comparação (ms)
            elapsed = max(
                0.000001,
                round((time.perf_counter() - start) * 1000, 6)
            )

            results.append({
                "method": "hashing_exato",
                "file_a": f1,
                "file_b": f2,

                "raw_score": 1 if is_dup else 0,
                "normalized_score": 1.0 if is_dup else 0.0,

                "is_exact_duplicate": is_dup,
                "is_near_duplicate": False,
                "is_strong_near_duplicate": False,

                "execution_time_ms": elapsed,
            })

    return results