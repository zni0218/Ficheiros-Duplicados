"""
text_simhash.py

Comparação baseada em SimHash para texto

- compara apenas ficheiros de texto
- usa distância Hamming entre hashes
- gera resultados completos (positivos e negativos)
"""

from itertools import combinations
import time
from pathlib import Path

from simhash import Simhash

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

def compute_distance(h1: str, h2: str) -> int:
    """
    Calcula distância entre dois SimHash.
    """
    return Simhash(int(h1)).distance(Simhash(int(h2)))


# COMPARAÇÃO VIA INDEX

def compare_from_index(index_data: dict, debug=False):
    """
    Compara ficheiros usando text_simhash.
    """

    results = []

    # filtrar apenas texto com fingerprint
    keys = [
        k for k, v in index_data.items()
        if v.get("text_simhash") and get_category(k) == "text"
    ]

    if debug:
        print(f"[DEBUG] text files: {len(keys)}")

    # comparar pares
    for f1, f2 in combinations(keys, 2):

        start = time.perf_counter()

        try:
            # calcular distância
            dist = compute_distance(
                index_data[f1]["text_simhash"],
                index_data[f2]["text_simhash"]
            )

        except Exception:
            continue

        # tempo por comparação (ms)
        elapsed = max(
            0.000001,
            round((time.perf_counter() - start) * 1000, 6)
        )

        # ground truth (hash exato)
        sha_match = (
            index_data[f1].get("hashing_exato") ==
            index_data[f2].get("hashing_exato")
        )

        # classificação
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