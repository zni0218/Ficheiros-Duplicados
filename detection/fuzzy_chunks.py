"""
fuzzy_chunks.py

Comparação baseada em chunk hashing

- usa similaridade de sequências
- aplicado apenas a texto e documentos
- gera resultados completos (positivos e negativos)
"""

from itertools import combinations
import time
import difflib
import ast
from pathlib import Path

from utils.score_utils import classify_score
from utils.file_utils import EXT_BY_CATEGORY


# CONFIG

# threshold de referência (não usado diretamente aqui)
THRESHOLD = 40.0


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


# SIMILARIDADE

def fuzzy_similarity(c1, c2):
    """
    Calcula similaridade entre listas de chunks.
    """

    if not c1 or not c2:
        return 0.0

    return difflib.SequenceMatcher(
        a=c1,
        b=c2
    ).ratio() * 100.0


# COMPARAÇÃO VIA INDEX

def compare_from_index(index_data: dict, debug=False):
    """
    Compara ficheiros usando fuzzy_chunks.
    """

    results = []

    # filtrar categorias relevantes
    allowed = {"text", "document"}

    keys = [
        k for k, v in index_data.items()
        if v.get("fuzzy_chunks") and get_category(k) in allowed
    ]

    if debug:
        print(f"[DEBUG] fuzzy_chunks keys: {len(keys)}")

    # comparar pares
    for f1, f2 in combinations(keys, 2):

        start = time.perf_counter()

        try:
            # converter string → lista
            chunks1 = ast.literal_eval(index_data[f1]["fuzzy_chunks"])
            chunks2 = ast.literal_eval(index_data[f2]["fuzzy_chunks"])

            # calcular similaridade
            raw_score = fuzzy_similarity(chunks1, chunks2)

        except Exception:
            continue

        # tempo por comparação (ms)
        elapsed = max(
            0.000001,
            round((time.perf_counter() - start) * 1000, 6)
        )

        # ground truth
        sha_match = (
            index_data[f1].get("hashing_exato") ==
            index_data[f2].get("hashing_exato")
        )

        # classificação
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
