"""
fuzzy_chunks.py

Comparação baseada em chunk hashing

"""

from itertools import combinations
import time
import difflib
import ast
from pathlib import Path

from utils.score_utils import classify_score
from utils.file_utils import EXT_BY_CATEGORY


# ======================================================
# CONFIGURAÇÃO
# ======================================================

# valor de referência (não utilizado diretamente aqui,
# mas pode ser usado em classificação externa)
THRESHOLD = 40.0


# ======================================================
# MAPEAMENTO EXTENSÃO → CATEGORIA
# ======================================================

# cria um dicionário para converter extensões em categorias
EXT_TO_CATEGORY = {}

for cat, exts in EXT_BY_CATEGORY.items():
    for e in exts:
        EXT_TO_CATEGORY[e] = cat


def get_category(path: str):
    """
    Determina a categoria do ficheiro com base na extensão.

    """
    ext = Path(path).suffix.lower()
    return EXT_TO_CATEGORY.get(ext, "unknown")


# ======================================================
# FUNÇÃO DE SIMILARIDADE
# ======================================================

def fuzzy_similarity(c1, c2):
    """
    Calcula similaridade entre duas listas de chunks.

    """

    # se algum estiver vazio → sem similaridade
    if not c1 or not c2:
        return 0.0

    return difflib.SequenceMatcher(a=c1, b=c2).ratio() * 100.0


# ======================================================
# COMPARAÇÃO PRINCIPAL
# ======================================================

def compare_from_index(index_data: dict, debug=False):
    """
    Compara ficheiros utilizando fuzzy chunk hashing.
    """

    results = []

    # selecionar ficheiros com dados disponíveis
    keys = [
        k for k, v in index_data.items()
        if v.get("fuzzy_chunks")
    ]

    if debug:
        print(f"[DEBUG] fuzzy_chunks keys: {len(keys)}")

    # gerar combinações de pares
    for f1, f2 in combinations(keys, 2):

        # comparar apenas ficheiros da mesma categoria
        if get_category(f1) != get_category(f2):
            continue

        start = time.perf_counter()

        try:
            # converter representação string → lista real
            chunks1 = ast.literal_eval(index_data[f1]["fuzzy_chunks"])
            chunks2 = ast.literal_eval(index_data[f2]["fuzzy_chunks"])

            # calcular similaridade
            raw_score = fuzzy_similarity(chunks1, chunks2)

        except Exception:
            # ignora erros de parsing ou dados inválidos
            continue

        # tempo de execução da comparação (em ms)
        elapsed = max(
            0.000001,
            round((time.perf_counter() - start) * 1000, 6)
        )

        # verificação de duplicado exato (ground truth)
        sha_match = (
            index_data[f1].get("hashing_exato") ==
            index_data[f2].get("hashing_exato")
        )

        # classificar resultado (normalização + flags)
        norm, is_exact, is_near, is_strong = classify_score(
            method="fuzzy_chunks",
            raw_score=raw_score,
            sha_match=sha_match
        )

        # registar resultado
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
