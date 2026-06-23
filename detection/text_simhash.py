"""
detection/text_simhash.py

✅ comparação de texto via SimHash
"""

from itertools import combinations
import time

from simhash import Simhash
from utils.score_utils import classify_score


MAX_DIST = 10


# ============================================================
# DISTÂNCIA
# ============================================================

def compute_distance(h1: str, h2: str) -> int:
    return Simhash(int(h1)).distance(Simhash(int(h2)))


# ============================================================
# COMPARAÇÃO VIA INDEX
# ============================================================

def compare_from_index(index_data: dict, debug=False):

    results = []

    keys = [
        k for k, v in index_data.items()
        if v.get("text_simhash")
    ]

    for f1, f2 in combinations(keys, 2):

        start = time.perf_counter()

        try:
            dist = compute_distance(
                index_data[f1]["text_simhash"],
                index_data[f2]["text_simhash"]
            )
        except Exception:
            continue

        elapsed = max(0.000001, round((time.perf_counter() - start) * 1000, 6))

        if dist > MAX_DIST:
            continue

        # ✅ ground truth
        sha_match = (
            index_data[f1].get("hashing_exato") ==
            index_data[f2].get("hashing_exato")
        )

        norm, is_exact, is_near, is_strong = classify_score(
            method="text_simhash",
            raw_score=int(dist),
            sha_match=sha_match
        )

        results.append({
            "method": "text_simhash",
            "file_a": f1,
            "file_b": f2,
            "raw_score": int(dist),
            "normalized_score": round(norm or 0.0, 4),
            "is_exact_duplicate": is_exact,
            "is_near_duplicate": is_near,
            "is_strong_near_duplicate": is_strong,
            "execution_time_ms": elapsed,
        })

    return results