"""
detection/fuzzy_chunks.py

✅ comparação fuzzy_chunks
✅ usa index (combined ou per-method)
"""

from itertools import combinations
import time
import difflib
import ast

from utils.score_utils import classify_score


THRESHOLD = 40.0


# ============================================================
# SIMILARIDADE
# ============================================================

def fuzzy_similarity(c1, c2):

    if not c1 or not c2:
        return 0.0

    return difflib.SequenceMatcher(a=c1, b=c2).ratio() * 100.0


# ============================================================
# COMPARAÇÃO VIA INDEX
# ============================================================

def compare_from_index(index_data: dict, debug=False):

    results = []

    keys = [
        k for k, v in index_data.items()
        if v.get("fuzzy_chunks")
    ]

    for f1, f2 in combinations(keys, 2):

        start = time.perf_counter()

        try:
            # ✅ usar ast.literal_eval (SEGURANÇA)
            chunks1 = ast.literal_eval(index_data[f1]["fuzzy_chunks"])
            chunks2 = ast.literal_eval(index_data[f2]["fuzzy_chunks"])

            raw_score = fuzzy_similarity(chunks1, chunks2)

        except Exception:
            continue

        elapsed = round((time.perf_counter() - start) * 1000, 6)

        if raw_score < THRESHOLD:
            continue

        sha_match = (
            index_data[f1].get("hashing_exato") ==
            index_data[f2].get("hashing_exato")
        )

        norm, is_exact, is_near, is_strong = classify_score(
            method="fuzzy_chunks",
            raw_score=raw_score,
            sha_match=sha_match
        )

        results.append({
            "method": "fuzzy_chunks",
            "file_a": f1,
            "file_b": f2,
            "raw_score": round(raw_score, 2),
            "normalized_score": round(norm or 0.0, 4),
            "is_exact_duplicate": is_exact,
            "is_near_duplicate": is_near,
            "is_strong_near_duplicate": is_strong,
            "execution_time_ms": elapsed,
        })

    return results