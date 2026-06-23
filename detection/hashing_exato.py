"""
detection/hashing_exato.py

✅ detecção de duplicados exatos via index
"""

from itertools import combinations
import time


# ============================================================
# DETEÇÃO VIA INDEX
# ============================================================

def compare_from_index(index_data: dict, debug=False):

    results = []

    # ✅ agrupar por hash
    hash_map = {}

    for path, data in index_data.items():

        h = data.get("hashing_exato")

        if not h:
            continue

        if h not in hash_map:
            hash_map[h] = []

        hash_map[h].append(path)

    # ✅ gerar pares
    for digest, files in hash_map.items():

        if len(files) < 2:
            continue

        for i in range(len(files)):
            for j in range(i + 1, len(files)):

                start = time.perf_counter()

                elapsed = max(
                    0.000001,
                    round((time.perf_counter() - start) * 1000, 6)
                )

                results.append({
                    "method": "hashing_exato",
                    "file_a": files[i],
                    "file_b": files[j],

                    "raw_score": 1,
                    "normalized_score": 1.0,

                    "is_exact_duplicate": True,
                    "is_near_duplicate": False,
                    "is_strong_near_duplicate": False,

                    "execution_time_ms": elapsed,
                })

    return results
