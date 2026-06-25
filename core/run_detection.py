"""
run_detection.py
Responsável pela fase de comparação (deteção de duplicados)
"""

# IMPORTS BASE

import csv

from pathlib import Path
from typing import Optional, List

# normalização de paths (windows-safe)
from utils.path_utils_safe import safe_path

# IMPORTS DOS MÉTODOS DE DETECTION


# cada módulo implementa:


from detection.hashing_exato import compare_from_index as detect_exact
from detection.fuzzy_chunks import compare_from_index as detect_fuzzy
from detection.image_phash import compare_from_index as detect_image
from detection.text_simhash import compare_from_index as detect_text
from detection.audio_phash import compare_from_index as detect_audio
from detection.video_phash import compare_from_index as detect_video
from detection.ssdeep_hash import compare_from_index as detect_ssdeep
from detection.tlsh_hash import compare_from_index as detect_tlsh



# LOAD INDEX

def load_index(csv_path: Path) -> dict:
    """
    Lê combined_index.csv e converte em dicionário.
    """

    data = {}

    # abre CSV
    with open(safe_path(csv_path), newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # percorre cada linha
        for row in reader:
            p = row["path"]

            # remove campos vazios
            clean = {k: v for k, v in row.items() if v}

            data[p] = clean

    return data


# SELF CHECK

def is_self_compare(a: str, b: str) -> bool:
    """
    Verifica se estamos a comparar o mesmo ficheiro.
    """
    return a == b

# MAIN

def run_detection(
    index_dir: Path,
    temp_dir: Optional[Path],
    methods: Optional[List[str]] = None,   # seleção de métodos
    debug: bool = False,
    stop_on_exact: bool = False
):

    # PATHS (dataset)
    # caminho para o index principal
    dataset_csv = index_dir / "dataset_index" / "combined_index.csv"

    if not dataset_csv.exists():
        raise RuntimeError(f"combined_index.csv não encontrado em: {dataset_csv}")

    # carrega index base
    dataset_index = load_index(dataset_csv)

    # marca todos como "não query"
    for k in dataset_index:
        dataset_index[k]["__query__"] = False

    # QUERY (modo interactive)
    query_index = {}
    if temp_dir:
        # caminho para index da query
        temp_csv = temp_dir / "dataset_index" / "combined_index.csv"

        if temp_csv.exists():
            query_index = load_index(temp_csv)

            # marca como query
            for k in query_index:
                query_index[k]["__query__"] = True

    has_query = len(query_index) > 0

    # MERGE (dataset + query)
    index_data = {}

    # base primeiro
    index_data.update(dataset_index)

    # depois query (pode sobrescrever)
    index_data.update(query_index)

    if debug:
        print(f"[DEBUG] base={len(dataset_index)} query={len(query_index)}")

    # MÉTODOS DISPONÍVEIS

    ALL_METHODS = {
        "hashing_exato": detect_exact,
        "fuzzy_chunks": detect_fuzzy,
        "image_phash": detect_image,
        "text_simhash": detect_text,
        "audio_phash": detect_audio,
        "video_phash": detect_video,
        "ssdeep": detect_ssdeep,
        "tlsh": detect_tlsh,
    }

    # seleção de métodos (igual ao build_index)

    if methods is None:
        selected_methods = ALL_METHODS
    else:
        selected_methods = {
            m: ALL_METHODS[m]
            for m in methods
            if m in ALL_METHODS
        }

    if debug:
        print(f"[DEBUG] métodos usados: {list(selected_methods.keys())}")

    # lista final de resultados
    all_results = []

    # LOOP DETECTION

    for name, func in selected_methods.items():

        if debug:
            print(f"[DEBUG] method: {name}")

        try:
            # executa método de comparação
            raw = func(index_data, debug=debug)
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            continue

        filtered = []

        # FILTRAGEM

        for r in raw:

            a = r["file_a"]
            b = r["file_b"]

            # flags de query
            a_q = index_data.get(a, {}).get("__query__", False)
            b_q = index_data.get(b, {}).get("__query__", False)

            # INTERACTIVE: apenas QUERY vs BASE

            if has_query:
                # aceita só comparações cruzadas
                if not ((a_q and not b_q) or (b_q and not a_q)):
                    continue

            # REMOVE SELF (A vs A)
            if is_self_compare(a, b):
                continue

            filtered.append(r)

        # junta ao resultado global
        all_results.extend(filtered)


        # EARLY STOP (apenas interactive + hashing_exato)


        if stop_on_exact and has_query and name == "hashing_exato":

            # se encontrou duplicado exato → para
            if any(r["is_exact_duplicate"] for r in filtered):

                if debug:
                    print("[DEBUG] early stop (exact)")

                break

    return all_results