"""
interactive_compare.py

"""

import time
import shutil
import csv

from pathlib import Path

# utilitários
from utils.path_utils_safe import safe_path

# módulos principais
from core.run_validation import run_validation
from core.build_index import build_index
from core.run_detection import run_detection


# CONFIG

# métodos rápidos
FAST_METHODS = ["hashing_exato"]

# métodos mais pesados
DEEP_METHODS = [
    "tlsh",
    "image_phash",
    "audio_phash",
    "text_simhash",
    "video_phash",
]

# todos os métodos
ALL_METHODS = FAST_METHODS + DEEP_METHODS


# PATHS

INTERACTIVE_DIR = Path("data/outputs/interactive")

SESSION_INDEX_DIR = INTERACTIVE_DIR / "session_index"
SESSION_DATASET_DIR = SESSION_INDEX_DIR / "dataset_index"

TEMP_QUERY_DIR = INTERACTIVE_DIR / "_temp_query"
TEMP_QUERY_DATASET = TEMP_QUERY_DIR / "dataset_index"

INPUTS_DIR = INTERACTIVE_DIR / "inputs"
VALIDATION_DIR = INTERACTIVE_DIR / "validation"
RESULTS_DIR = INTERACTIVE_DIR / "results"


# INIT

def init():

    # limpar sessão
    if SESSION_INDEX_DIR.exists():
        shutil.rmtree(SESSION_INDEX_DIR)

    # limpar inputs
    if INPUTS_DIR.exists():
        shutil.rmtree(INPUTS_DIR)

    # limpar query temporária
    if TEMP_QUERY_DIR.exists():
        shutil.rmtree(TEMP_QUERY_DIR)

    # limpar resultados
    if RESULTS_DIR.exists():
        shutil.rmtree(RESULTS_DIR)

    # recriar estrutura
    SESSION_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# CSV

def write_csv(path: Path, rows):

    # ignora vazio
    if not rows:
        return

    exists = path.exists()

    with open(safe_path(path), "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())

        # header
        if not exists:
            writer.writeheader()

        writer.writerows(rows)


# PROCESS RESULTS

def process_results(results):

    exact, near, strong = [], [], []

    for r in results:

        # normalizar duplicado exato
        if r.get("raw_score") == 1.0:
            r["is_exact_duplicate"] = True
            r["is_near_duplicate"] = True

        # classificação
        if r["is_exact_duplicate"]:
            exact.append(r)

        elif r.get("is_strong_near_duplicate", False):
            strong.append(r)
            near.append(r)

        elif r["is_near_duplicate"]:
            near.append(r)

    return exact, near, strong


# MAIN

def interactive_mode():

    print("\n=== INTERACTIVE ===\n")

    # inicializar sessão
    init()

    while True:

        inp = input("file> ").strip()

        # sair
        if inp == "0":
            break

        p = Path(inp)

        if not p.exists():
            print("[ERRO]")
            continue

        p = Path(safe_path(p))

        start = time.perf_counter()

        # VALIDATION

        validation = run_validation(p, VALIDATION_DIR, temp_mode=True)

        if not validation["valid_files"]:
            print("[INVALID]")
            continue

        session_csv = SESSION_DATASET_DIR / "combined_index.csv"

        # PRIMEIRO FICHEIRO

        if not session_csv.exists():

            print("[INFO] primeiro ficheiro → inicializar sessão")

            # copiar para sessão
            dst = INPUTS_DIR / p.name
            shutil.copy2(p, dst)

            # criar index inicial completo
            build_index(
                base=[dst],
                out=SESSION_DATASET_DIR,
                methods=ALL_METHODS
            )

            results = []

        # BASE EXISTE

        else:

            # limpar query temporária
            if TEMP_QUERY_DIR.exists():
                shutil.rmtree(TEMP_QUERY_DIR)

            TEMP_QUERY_DATASET.mkdir(parents=True, exist_ok=True)

            # FASE 1: FAST INDEX

            build_index(
                base=p,
                out=TEMP_QUERY_DATASET,
                methods=FAST_METHODS
            )

            # FASE 1: FAST DETECTION

            results_fast = run_detection(
                index_dir=SESSION_INDEX_DIR,
                temp_dir=TEMP_QUERY_DIR,
                methods=FAST_METHODS,
                stop_on_exact=True
            )

            exact_fast, _, _ = process_results(results_fast)

            # duplicado encontrado → parar
            if exact_fast:
                results = results_fast

            # FASE 2: DEEP

            else:

                build_index(
                    base=p,
                    out=TEMP_QUERY_DATASET,
                    methods=DEEP_METHODS
                )

                results_deep = run_detection(
                    index_dir=SESSION_INDEX_DIR,
                    temp_dir=TEMP_QUERY_DIR,
                    methods=DEEP_METHODS,
                    stop_on_exact=False
                )

                results = results_fast + results_deep

        # PROCESS

        exact, near, strong = process_results(results)

        # OUTPUT

        if session_csv.exists():

            if exact:
                print("[DUPLICATE]")

            elif strong:
                print("[STRONG]")

            elif near:
                print("[SIMILAR]")

            else:
                print("[INFO] sem matches")

        # SAVE

        write_csv(RESULTS_DIR / "ALL_combined.csv", results)

        # ADD AO SESSION

        if session_csv.exists() and not exact:

            dst = INPUTS_DIR / p.name

            # evitar duplicados na sessão
            if not dst.exists():
                shutil.copy2(p, dst)

                build_index(
                    base=[dst],
                    out=SESSION_DATASET_DIR,
                    methods=ALL_METHODS
                )

        # tempo total por input (ms)
        elapsed = (time.perf_counter() - start) * 1000

        print(f" {elapsed:.2f} ms\n")


# RUN

if __name__ == "__main__":
    interactive_mode()