"""
interactive_compare.py

Modo interativo para deteção de duplicados.

FUNCIONALIDADES:
- Entrada de ficheiros um a um (simula ambiente real)
- Sessão incremental → guarda histórico
- Comparação FAST (rápida) + DEEP (profunda)
- Suporte opcional a índice global (run_all)

OBJETIVO:
Simular receção contínua de ficheiros
"""

import time
import shutil
import csv
import argparse
from pathlib import Path

# utilitário para normalizar paths (evita problemas Windows)
from utils.path_utils_safe import safe_path

# módulos principais do pipeline
from core.run_validation import run_validation
from core.build_index import build_index
from core.run_detection import run_detection


# Métodos rápidos (FAST)
# → usados primeiro para detetar duplicados exatos rapidamente
FAST_METHODS = ["hashing_exato"]

# Métodos mais pesados (DEEP)
# → usados apenas se FAST não encontrar duplicados
DEEP_METHODS = [
    "tlsh",
    "image_phash",
    "audio_phash",
    "text_simhash",
    "video_phash",
]

# Todos os métodos (usados para index completo da sessão)
ALL_METHODS = FAST_METHODS + DEEP_METHODS


# raiz do projeto (ex: scripts_teste)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# índice global (gerado pelo run_all)
GLOBAL_INDEX_PATH = PROJECT_ROOT / "data" / "outputs" / "run_all"

# diretoria principal do modo interativo
INTERACTIVE_DIR = PROJECT_ROOT / "data" / "outputs" / "interactive"

# sessão atual (onde se guarda o estado incremental)
SESSION_INDEX_DIR = INTERACTIVE_DIR / "session_index"
SESSION_DATASET_DIR = SESSION_INDEX_DIR / "dataset_index"

# diretoria temporária para o ficheiro atual
TEMP_QUERY_DIR = INTERACTIVE_DIR / "_temp_query"
TEMP_QUERY_DATASET = TEMP_QUERY_DIR / "dataset_index"

# outras pastas auxiliares
INPUTS_DIR = INTERACTIVE_DIR / "inputs"
VALIDATION_DIR = INTERACTIVE_DIR / "validation"
RESULTS_DIR = INTERACTIVE_DIR / "results"


def init():
    """
    Reinicia completamente a sessão interativa.

    Remove:
    - histórico anterior
    - ficheiros já inseridos
    - resultados
    - índices temporários

    Cria uma estrutura limpa para nova execução.
    """

    for d in [SESSION_INDEX_DIR, INPUTS_DIR, TEMP_QUERY_DIR, RESULTS_DIR]:
        if d.exists():
            shutil.rmtree(d)

    SESSION_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)




def write_csv(path: Path, rows):
    """
    Guarda resultados em CSV.

    - Modo append (não apaga ficheiro anterior)
    - Cria header automaticamente se necessário
    """

    if not rows:
        return

    exists = path.exists()

    with open(safe_path(path), "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())

        # escreve cabeçalho apenas na primeira vez
        if not exists:
            writer.writeheader()

        writer.writerows(rows)



def process_results(results):
    """
    Classifica resultados em três categorias:

    - duplicados exatos
    - semelhantes
    - semelhantes fortes

    Também normaliza scores (ex: raw_score == 1 → duplicado)
    """

    exact, near, strong = [], [], []

    for r in results:

        # normalização automática
        if r.get("raw_score") == 1.0:
            r["is_exact_duplicate"] = True
            r["is_near_duplicate"] = True

        if r["is_exact_duplicate"]:
            exact.append(r)

        elif r.get("is_strong_near_duplicate", False):
            strong.append(r)
            near.append(r)

        elif r["is_near_duplicate"]:
            near.append(r)

    return exact, near, strong


def detect_with_indexes(index_dirs, temp_dir, methods, stop_on_exact):
    """
    Executa detection em múltiplos índices:

    - sessão atual
    - índice global (se ativado)

    Para cada resultado:
    adiciona campo 'source' → origem do match
    """

    all_results = []

    for idx in index_dirs:

        results = run_detection(
            index_dir=idx,
            temp_dir=temp_dir,
            methods=methods,
            stop_on_exact=stop_on_exact
        )

        # marcar origem do resultado
        for r in results:
            r["source"] = "global" if idx == GLOBAL_INDEX_PATH else "session"

        all_results.extend(results)

    return all_results



def interactive_mode(use_global):
    """
    Loop principal do modo interativo.

    Fluxo:
    INPUT → VALIDATION → FAST → (STOP ou DEEP) → RESULTADO → UPDATE SESSÃO
    """

    print("\n=== INTERACTIVE MODE ===\n")

    # inicializar sessão limpa
    init()

    while True:

        # receber input do utilizador
        inp = input("file> ").strip()

        # sair
        if inp == "0":
            break

        p = Path(inp)

        # validar existência
        if not p.exists():
            print("[ERRO]")
            continue

        p = Path(safe_path(p))
        start = time.perf_counter()

        # VALIDAÇÃO DO FICHEIRO

        validation = run_validation(p, VALIDATION_DIR, temp_mode=True)

        if not validation["valid_files"]:
            print("[INVALID]")
            continue

        session_csv = SESSION_DATASET_DIR / "combined_index.csv"

        # lista de índices a usar
        index_dirs = [SESSION_INDEX_DIR]

        if use_global:
            index_dirs.append(GLOBAL_INDEX_PATH)

        # PRIMEIRO FICHEIRO


        if not session_csv.exists():

            print("[INFO] primeiro ficheiro")

            # adicionar à sessão
            dst = INPUTS_DIR / p.name
            shutil.copy2(p, dst)

            # criar index inicial
            build_index([dst], SESSION_DATASET_DIR, ALL_METHODS)

            results = []

            # se global ativo → tentar detectar imediatamente
            if use_global:

                # limpar query anterior
                if TEMP_QUERY_DIR.exists():
                    shutil.rmtree(TEMP_QUERY_DIR)

                TEMP_QUERY_DATASET.mkdir(parents=True, exist_ok=True)

                # FAST
                build_index(p, TEMP_QUERY_DATASET, FAST_METHODS)

                results_fast = detect_with_indexes(
                    [GLOBAL_INDEX_PATH],
                    TEMP_QUERY_DIR,
                    FAST_METHODS,
                    True
                )

                exact_fast, _, _ = process_results(results_fast)

                if exact_fast:
                    results = results_fast
                else:
                    # DEEP
                    build_index(p, TEMP_QUERY_DATASET, DEEP_METHODS)

                    results_deep = detect_with_indexes(
                        [GLOBAL_INDEX_PATH],
                        TEMP_QUERY_DIR,
                        DEEP_METHODS,
                        False
                    )

                    results = results_fast + results_deep


        # RESTANTES FICHEIROS


        else:

            if TEMP_QUERY_DIR.exists():
                shutil.rmtree(TEMP_QUERY_DIR)

            TEMP_QUERY_DATASET.mkdir(parents=True, exist_ok=True)

            # FAST
            build_index(p, TEMP_QUERY_DATASET, FAST_METHODS)

            results_fast = detect_with_indexes(
                index_dirs,
                TEMP_QUERY_DIR,
                FAST_METHODS,
                True
            )

            exact_fast, _, _ = process_results(results_fast)

            # se encontrou duplicado → não precisa DEEP
            if exact_fast:
                results = results_fast
            else:
                # DEEP
                build_index(p, TEMP_QUERY_DATASET, DEEP_METHODS)

                results_deep = detect_with_indexes(
                    index_dirs,
                    TEMP_QUERY_DIR,
                    DEEP_METHODS,
                    False
                )

                results = results_fast + results_deep

        # CLASSIFICAÇÃO FINAL


        exact, near, strong = process_results(results)

        # mostrar resultado
        if session_csv.exists():

            src = results[0]["source"] if results else "session"

            if exact:
                print(f"[DUPLICATE ({src})]")
            elif strong:
                print(f"[STRONG ({src})]")
            elif near:
                print(f"[SIMILAR ({src})]")
            else:
                print("[INFO] sem matches")

        # guardar resultados
        write_csv(RESULTS_DIR / "ALL_combined.csv", results)

        # UPDATE DA SESSÃO

        if session_csv.exists() and not exact:

            dst = INPUTS_DIR / p.name

            # evitar duplicar ficheiros
            if not dst.exists():
                shutil.copy2(p, dst)

                build_index([dst], SESSION_DATASET_DIR, ALL_METHODS)

        # tempo total
        elapsed = (time.perf_counter() - start) * 1000
        print(f"{elapsed:.2f} ms\n")


# CLI (EXECUÇÃO)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--use-global",
        action="store_true",
        help="Ativar índice global (run_all)"
    )

    args = parser.parse_args()

    use_global = args.use_global

    # verificar global
    if use_global:
        if not GLOBAL_INDEX_PATH.exists():
            print("[WARN] Global index não encontrado")
            use_global = False
        else:
            print("[INFO] Global ON")
    else:
        print("[INFO] Global OFF")

    interactive_mode(use_global)