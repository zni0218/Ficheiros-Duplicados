"""
detection/ssdeep_hash.py

✅ comparação fuzzy via ssdeep (index-based)
"""

from itertools import combinations
import time

try:
    import ssdeep
except Exception:
    ssdeep = None

from utils.score_utils import classify_score


THRESHOLD = 70


# ============================================================
# COMPARAÇÃO VIA INDEX
# ============================================================

def compare_from_index(index_data: dict, debug=False):

    if ssdeep is None:
        return []

    results = []

    keys = [
        k for k, v in index_data.items()
        if v.get("ssdeep")
    ]

    for f1, f2 in combinations(keys, 2):

        start = time.perf_counter()

        try:
            raw_score = ssdeep.compare(
                index_data[f1]["ssdeep"],
                index_data[f2]["ssdeep"]
            )
        except Exception:
            continue

        elapsed = max(
            0.000001,
            round((time.perf_counter() - start) * 1000, 6)
        )

        if raw_score < THRESHOLD:
            continue

        # ✅ verdade absoluta
        sha_match = (
            index_data[f1].get("hashing_exato") ==
            index_data[f2].get("hashing_exato")
        )

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