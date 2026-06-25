"""
audio_phash.py

Comparação perceptual para áudio

- usa pHash do espectrograma
- compara apenas ficheiros de áudio
- gera resultados completos (positivos e negativos)
"""

from itertools import combinations
import time
from pathlib import Path

import imagehash

from utils.score_utils import classify_score
from utils.file_utils import EXT_BY_CATEGORY


# CONFIG

# distância máxima esperada (referência)
MAX_DIST = 20


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

def compare_hashes(h1: str, h2: str) -> int:
    """
    Calcula distância entre dois hashes.
    """
    return imagehash.hex_to_hash(h1) - imagehash.hex_to_hash(h2)


# COMPARAÇÃO VIA INDEX

def compare_from_index(index_data: dict, debug: bool = False):
    """
    Compara ficheiros de áudio usando audio_phash.
    """

    results = []

    # filtrar apenas áudio com fingerprint
    keys = [
        k for k, v in index_data.items()
        if v.get("audio_phash") and get_category(k) == "audio"
    ]

    if debug:
        print(f"[DEBUG] audio files: {len(keys)}")

    # comparar pares
    for f1, f2 in combinations(keys, 2):

        start = time.perf_counter()

        try:
            # calcular distância
            dist = compare_hashes(
                index_data[f1]["audio_phash"],
                index_data[f2]["audio_phash"]
            )

        except Exception:
            continue

        # tempo por comparação (ms)
        elapsed = max(
            0.000001,
            round((time.perf_counter() - start) * 1000, 6)
        )

        # ground truth (duplicado exato)
        sha_match = (
            index_data[f1].get("hashing_exato") ==
            index_data[f2].get("hashing_exato")
        )

        # classificação
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