"""
detection/audio_phash.py

✅ comparação de fingerprints
✅ usa dados do index (combined ou per-method)
"""

from itertools import combinations
import time

import imagehash

from utils.score_utils import classify_score


MAX_DIST = 12


# ============================================================
# DISTÂNCIA
# ============================================================

def compare_hashes(h1: str, h2: str) -> int:
    return imagehash.hex_to_hash(h1) - imagehash.hex_to_hash(h2)


# ============================================================
# VIA INDEX (USADO NO run_detection)
# ============================================================

def compare_from_index(index_data: dict, debug: bool = False):

    results = []

    keys = [
        k for k, v in index_data.items()
        if v.get("audio_phash")
    ]

    for f1, f2 in combinations(keys, 2):

        start = time.perf_counter()

        try:
            dist = compare_hashes(
                index_data[f1]["audio_phash"],
                index_data[f2]["audio_phash"]
            )
        except:
            continue

        elapsed = max(0.000001, round((time.perf_counter() - start) * 1000, 6))

        if dist > MAX_DIST:
            continue

        sha_match = (
            index_data[f1].get("hashing_exato") ==
            index_data[f2].get("hashing_exato")
        )

        norm, is_exact, is_near, is_strong = classify_score(
            method="audio_phash",
            raw_score=int(dist),
            sha_match=sha_match
        )

        results.append({
            "method": "audio_phash",
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
