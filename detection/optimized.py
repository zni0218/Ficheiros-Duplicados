"""
optimized.py

Comparação otimizada baseada em combinação de métodos

"""

from itertools import combinations
import time
from pathlib import Path

from utils.score_utils import compute_combined_score, classify_final
from utils.file_utils import EXT_BY_CATEGORY


# MAP EXT → CATEGORY

EXT_TO_CATEGORY = {}

for cat, exts in EXT_BY_CATEGORY.items():
    for e in exts:
        EXT_TO_CATEGORY[e] = cat


def get_category(path):
    """
    Obtém categoria a partir da extensão.
    """
    return EXT_TO_CATEGORY.get(Path(path).suffix.lower(), "unknown")


# MAIN

def compare_from_index(index_data: dict, debug=False):
    """
    Compara ficheiros usando pipeline otimizado.
    """

    results = []

    keys = list(index_data.keys())

    for f1, f2 in combinations(keys, 2):

        start = time.perf_counter()

        data1 = index_data[f1]
        data2 = index_data[f2]

        cat1 = get_category(f1)
        cat2 = get_category(f2)

        # comparar apenas dentro da mesma categoria
        if cat1 != cat2:
            continue

        # HASH EXACT (ground truth base)

        sha_match = (
            data1.get("hashing_exato") ==
            data2.get("hashing_exato")
        )

        # MÉTODOS POR CATEGORIA

        scores = {}

        if cat1 == "image":
            methods = ["image_phash"]

        elif cat1 == "audio":
            methods = ["audio_phash"]

        elif cat1 == "video":
            methods = ["video_phash"]

        elif cat1 == "text":
            methods = ["text_simhash"]

        else:
            methods = []

        # CALCULAR SCORES

        for m in methods:

            v1 = data1.get(m)
            v2 = data2.get(m)

            if not v1 or not v2:
                continue

            try:
                # diferença direta (já normalizado no index)
                raw_score = abs(float(v1) - float(v2))

                # converter para similaridade
                norm = 1 - raw_score

                scores[m] = norm

            except Exception:
                continue

        # COMBINAR SCORES

        combined_score = compute_combined_score(scores, sha_match)

        # CLASSIFICAÇÃO FINAL

        source_type, near_all, near_exclusive, strong_near = classify_final(
            combined_score,
            sha_match
        )

        # tempo por comparação (ms)
        elapsed = max(
            0.000001,
            (time.perf_counter() - start) * 1000
        )

        results.append({
            "method": "optimized",
            "file_a": f1,
            "file_b": f2,
            "raw_score": round(combined_score, 4),
            "normalized_score": round(combined_score, 4),
            "is_exact_duplicate": sha_match,
            "is_near_duplicate": near_exclusive,
            "is_strong_near_duplicate": strong_near,
            "execution_time_ms": round(elapsed, 6),
        })

    return results