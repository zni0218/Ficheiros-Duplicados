"""
detection/tlsh_hash.py

✅ comparação TLSH via index
"""

from itertools import combinations
import time

try:
    import tlsh
except Exception:
    tlsh = None

from utils.score_utils import classify_score


MAX_DIST = 30


# ============================================================
# COMPARAÇÃO VIA INDEX
# ============================================================

def compare_from_index(index_data: dict, debug=False):

    if tlsh is None:
        return []

    results = []

    keys = [
        k for k, v in index_data.items()
        if v.get("tlsh") and v.get("tlsh") != "TNULL"
    ]

    for f1, f2 in combinations(keys, 2):

        start = time.perf_counter()

        try:
            raw_score = tlsh.diff(
                index_data[f1]["tlsh"],
                index_data[f2]["tlsh"]
            )
        except Exception:
            continue

        elapsed = max(
            0.000001,
            round((time.perf_counter() - start) * 1000, 6)
        )

        if raw_score > MAX_DIST:
            continue

        # ✅ truth real
        sha_match = (
            index_data[f1].get("hashing_exato") ==
            index_data[f2].get("hashing_exato")
        )

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