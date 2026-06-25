"""
video_phash.py

Comparação perceptual para vídeo

- usa listas de pHash por frame
- compara apenas ficheiros vídeo
- gera resultados para benchmark
"""

from itertools import combinations
import time
import ast
from pathlib import Path

import imagehash

from utils.score_utils import classify_score
from utils.file_utils import EXT_BY_CATEGORY


# CONFIG

# distância máxima esperada (não usada diretamente aqui)
MAX_DIST = 12


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


# DISTÂNCIA

def mean_distance(list1, list2):
    """
    Calcula distância média entre listas de hashes.
    """

    if not list1 or not list2:
        return float("inf")

    dists = []

    for a, b in zip(list1, list2):
        dists.append(
            imagehash.hex_to_hash(a) - imagehash.hex_to_hash(b)
        )

    return sum(dists) / len(dists)


# COMPARAÇÃO VIA INDEX

def compare_from_index(index_data: dict, debug=False):
    """
    Compara vídeos com base em video_phash.
    """

    results = []

    # filtrar apenas vídeos com fingerprint
    keys = [
        k for k, v in index_data.items()
        if v.get("video_phash") and get_category(k) == "video"
    ]

    if debug:
        print(f"[DEBUG] video files: {len(keys)}")

    # comparar pares
    for v1, v2 in combinations(keys, 2):

        start = time.perf_counter()

        try:
            # converter strings → listas
            list1 = ast.literal_eval(index_data[v1]["video_phash"])
            list2 = ast.literal_eval(index_data[v2]["video_phash"])

            # calcular distância
            raw_score = mean_distance(list1, list2)

        except Exception:
            continue

        # tempo por comparação (ms)
        elapsed = max(
            0.000001,
            round((time.perf_counter() - start) * 1000, 6)
        )

        # ground truth (duplicado perfeito)
        sha_match = (
            index_data[v1].get("hashing_exato") ==
            index_data[v2].get("hashing_exato")
        )

        # classificação
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