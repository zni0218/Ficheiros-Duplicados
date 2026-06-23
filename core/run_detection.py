"""
run_detection.py

Detecção baseada em índices (combined_index).

✅ usa combined_index.csv
✅ suporta modo dataset + temp
✅ integra todos os métodos
"""

import csv
from pathlib import Path

from utils.path_utils_safe import safe_path

# ✅ IMPORTS DETECTION
from detection.hashing_exato import compare_from_index as detect_exact
from detection.fuzzy_chunks import compare_from_index as detect_fuzzy
from detection.image_phash import compare_from_index as detect_image
from detection.text_simhash import compare_from_index as detect_text
from detection.audio_phash import compare_from_index as detect_audio
from detection.video_phash import compare_from_index as detect_video
from detection.ssdeep_hash import compare_from_index as detect_ssdeep
from detection.tlsh_hash import compare_from_index as detect_tlsh


# ============================================================
# LOAD INDEX
# ============================================================

def load_index(csv_path: Path) -> dict:
    """
    CSV → dict:
        {
            path: {colunas}
        }
    """

    data = {}

    with open(safe_path(csv_path), newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            path = row["path"]

            # remover vazios
            clean = {k: v for k, v in row.items() if v}

            data[path] = clean

    return data


# ============================================================
# MERGE INDEX (dataset + temp)
# ============================================================

def merge_indexes(base_index: dict, temp_index: dict) -> dict:
    """
    junta index original + temp
    """

    merged = dict(base_index)

    for k, v in temp_index.items():
        merged[k] = v

    return merged


# ============================================================
# MAIN DETECTION
# ============================================================

def run_detection(
    index_dir: Path,
    temp_dir: Path,
    debug: bool = False
):

    # --------------------------------------------------------
    # LOAD DATASET INDEX
    # --------------------------------------------------------

    dataset_csv = index_dir / "combined_index.csv"

    if not dataset_csv.exists():
        raise RuntimeError("combined_index.csv não encontrado")

    dataset_index = load_index(dataset_csv)

    # --------------------------------------------------------
    # LOAD TEMP INDEX (OPCIONAL)
    # --------------------------------------------------------

    temp_index = {}

    if temp_dir:

        temp_csv = temp_dir / "combined_index.csv"

        if temp_csv.exists():
            temp_index = load_index(temp_csv)

    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    if temp_index:
        index_data = merge_indexes(dataset_index, temp_index)
    else:
        index_data = dataset_index

    if debug:
        print(f"[DEBUG] dataset: {len(dataset_index)}")
        print(f"[DEBUG] temp: {len(temp_index)}")
        print(f"[DEBUG] total: {len(index_data)}")

    # --------------------------------------------------------
    # RUN METHODS
    # --------------------------------------------------------

    all_results = []

    methods = [
        ("hashing_exato", detect_exact),
        ("fuzzy_chunks", detect_fuzzy),
        ("image_phash", detect_image),
        ("text_simhash", detect_text),
        ("audio_phash", detect_audio),
        ("video_phash", detect_video),
        ("ssdeep", detect_ssdeep),
        ("tlsh", detect_tlsh),
    ]

    for name, func in methods:

        if debug:
            print(f"[DEBUG] detection: {name}")

        try:
            results = func(index_data, debug=debug)
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            continue

        all_results.extend(results)

    return all_results
