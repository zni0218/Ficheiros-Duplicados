"""
detection/video_phash.py

✅ comparação de vídeos via pHash (keyframes)
"""

from itertools import combinations
import time
import ast

import imagehash

from utils.score_utils import classify_score


MAX_DIST = 12


# ============================================================
# DISTÂNCIA
# ============================================================

def mean_distance(list1, list2):

    if not list1 or not list2:
        return float("inf")

    dists = []

    for a, b in zip(list1, list2):
        dists.append(
            imagehash.hex_to_hash(a) - imagehash.hex_to_hash(b)
        )

    return sum(dists) / len(dists)


# ============================================================
# COMPARAÇÃO VIA INDEX
# ============================================================

def compare_from_index(index_data: dict, debug=False):

    results = []

    keys = [
        k for k, v in index_data.items()
        if v.get("video_phash")
    ]

    for v1, v2 in combinations(keys, 2):

        start = time.perf_counter()

        try:
            list1 = ast.literal_eval(index_data[v1]["video_phash"])
            list2 = ast.literal_eval(index_data[v2]["video_phash"])

            raw_score = mean_distance(list1, list2)

        except Exception:
            continue

        elapsed = max(
            0.000001,
            round((time.perf_counter() - start) * 1000, 6)
        )

        if raw_score > MAX_DIST:
            continue

        # ✅ truth REAL
        sha_match = (
            index_data[v1].get("hashing_exato") ==
            index_data[v2].get("hashing_exato")
        )

        norm, is_exact, is_near, is_strong = classify_score(
            method="video_phash",
            raw_score=raw_score,
            sha_match=sha_match
        )

        results.append({
            "method": "video_phash",
            "file_a": v1,
            "file_b": v2,
            "raw_score": round(raw_score, 3),
            "normalized_score": round(norm or 0.0, 4),
            "is_exact_duplicate": is_exact,
            "is_near_duplicate": is_near,
            "is_strong_near_duplicate": is_strong,
            "execution_time_ms": elapsed,
        })

    return results