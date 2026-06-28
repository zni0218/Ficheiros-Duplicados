"""
run_optimized.py

Pipeline otimizado:

- validação de ficheiros
- construção de índice completo
- deteção com estratégia FAST → DEEP (por par)

OBJETIVO:
Reduzir custo computacional, evitando aplicar métodos pesados
em ficheiros já identificados como duplicados exatos.
"""


# IMPORTS BASE

import argparse
import csv
import time

# manipulação de paths
from pathlib import Path

# utilitário para normalizar paths (compatibilidade Windows)
from utils.path_utils_safe import safe_path

# módulos principais do pipeline
from core.run_validation import run_validation
from core.build_index import build_index
from core.run_detection import run_detection



# CONFIGURAÇÃO DE MÉTODOS


# Métodos rápidos (FAST)
# → usados para deteção imediata de duplicados exatos
FAST_METHODS = ["hashing_exato"]

# Métodos mais pesados (DEEP)
# → usados apenas quando FAST não resolve o caso
DEEP_METHODS = [
    "tlsh",
    "image_phash",
    "text_simhash",
    "audio_phash",
    "video_phash",
]

# Todos os métodos (usados na construção do índice)
ALL_METHODS = FAST_METHODS + DEEP_METHODS



# UTILITÁRIO CSV


def write_csv(path: Path, rows):
    """
    Guarda dados em CSV.

    - Sobrescreve ficheiro existente
    - Cria header automaticamente
    """

    if not rows:
        return

    with open(safe_path(path), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# PIPELINE PRINCIPAL


def run_optimized(base: Path, out: Path, debug=False):
    """
    Executa pipeline otimizado completo:

    1) validação
    2) indexação (todos os métodos)
    3) deteção FAST → DEEP (por par)
    4) geração de resultados e métricas
    """

    # normalizar paths
    base = Path(safe_path(base))
    out = Path(safe_path(out))

    # criar diretoria base
    out.mkdir(parents=True, exist_ok=True)

    # estrutura de diretórios
    idx_dir = out / "dataset_index"
    res_dir = out / "results"
    perf_dir = out / "performance"

    for d in [idx_dir, res_dir, perf_dir]:
        d.mkdir(exist_ok=True)

    # timer global
    pipeline_start = time.perf_counter()


    # VALIDATION


    t0 = time.perf_counter()

    validation = run_validation(
        base=base,
        out=out / "validation",
        debug=debug,
        temp_mode=False
    )

    # ficheiros válidos
    valid_files = validation["valid_files"]

    # tempo da fase
    t_validation = time.perf_counter() - t0

    # abortar se vazio
    if not valid_files:
        print("[ERROR] Nenhum ficheiro válido")
        return

    # BUILD INDEX


    t0 = time.perf_counter()

    # gerar fingerprints para todos os métodos
    index_info = build_index(
        base=base,
        out=out,
        methods=ALL_METHODS,
        debug=debug
    )

    # tempo total de indexação
    t_index = time.perf_counter() - t0

    # tempos por método (já em segundos)
    index_times = index_info.get("method_times", {})


    # DETECTION (FAST → DEEP POR PAR)


    t0 = time.perf_counter()

    # -----------------------------
    # FASE 1: FAST
    # -----------------------------

    # aplicar métodos rápidos (hashing exato)
    results_fast = run_detection(
        index_dir=out,
        temp_dir=None,
        methods=FAST_METHODS,
        debug=debug
    )

    # identificar pares já resolvidos (duplicados exatos)
    exact_pairs = set()

    for r in results_fast:
        if r.get("is_exact_duplicate"):
            pair = tuple(sorted([r["file_a"], r["file_b"]]))
            exact_pairs.add(pair)

    # -----------------------------
    # FASE 2: DEEP
    # -----------------------------

    # aplicar métodos mais pesados
    results_deep = run_detection(
        index_dir=out,
        temp_dir=None,
        methods=DEEP_METHODS,
        debug=debug
    )

    # filtrar resultados deep:
    # → ignorar pares já identificados como duplicados exatos
    filtered_deep = []

    for r in results_deep:

        pair = tuple(sorted([r["file_a"], r["file_b"]]))

        if pair in exact_pairs:
            continue  # skip

        filtered_deep.append(r)

    # combinar resultados finais
    results = results_fast + filtered_deep

    # tempo de deteção
    t_detection = time.perf_counter() - t0


    # ORGANIZAÇÃO DOS RESULTADOS

    per_method = {}
    exact_rows = []
    near_rows = []
    strong_rows = []

    for r in results:

        # normalizar estrutura
        row = {
            "method": r["method"],
            "file_a": r["file_a"],
            "file_b": r["file_b"],
            "raw_score": r["raw_score"],
            "normalized_score": r["normalized_score"],
            "is_exact_duplicate": r["is_exact_duplicate"],
            "is_near_duplicate": r["is_near_duplicate"],
            "is_strong_near_duplicate": r.get("is_strong_near_duplicate", False),
            "execution_time_ms": r["execution_time_ms"],
        }

        m = row["method"]

        # agrupar por método
        per_method.setdefault(m, []).append(row)

        # classificação
        if row["is_exact_duplicate"]:
            exact_rows.append(row)
        elif row["is_strong_near_duplicate"]:
            strong_rows.append(row)
            near_rows.append(row)
        elif row["is_near_duplicate"]:
            near_rows.append(row)


    # ESCRITA DOS RESULTADOS


    # ficheiros por método
    for method, rows in per_method.items():
        write_csv(res_dir / f"{method}.csv", rows)

    # ficheiros agregados
    write_csv(res_dir / "ALL_exact.csv", exact_rows)
    write_csv(res_dir / "ALL_near.csv", near_rows)
    write_csv(res_dir / "ALL_strong_near.csv", strong_rows)

    # ficheiro completo
    write_csv(res_dir / "ALL_combined.csv", results)


    # PERFORMANCE POR MÉTODO

    detection_times = {}
    method_perf = []

    # somar tempos de detection
    for r in results:
        m = r["method"]
        detection_times.setdefault(m, 0)
        detection_times[m] += r["execution_time_ms"]

    # juntar index + detection
    for m in ALL_METHODS:

        idx_t = index_times.get(m, 0)
        det_t = detection_times.get(m, 0) / 1000

        method_perf.append({
            "method": m,
            "index_time_s": round(idx_t, 4),
            "detection_time_s": round(det_t, 4),
            "total_time_s": round(idx_t + det_t, 4)
        })

    write_csv(perf_dir / "performance_methods.csv", method_perf)

    # PERFORMANCE GLOBAL


    total_time = time.perf_counter() - pipeline_start

    write_csv(
        perf_dir / "performance_global.csv",
        [{
            "total_pipeline_time_s": round(total_time, 4),
            "validation_s": round(t_validation, 4),
            "index_s": round(t_index, 4),
            "detection_s": round(t_detection, 4),
            "total_files": len(valid_files)
        }]
    )

    print(f"[OK] Optimized pipeline em {total_time:.4f}s")



# CLI


if __name__ == "__main__":

    # raiz do projeto
    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser()

    # diretoria de entrada
    parser.add_argument(
        "--base",
        default=str(PROJECT_ROOT / "data/original_files")
    )

    # diretoria de output
    parser.add_argument(
        "--out",
        default=str(PROJECT_ROOT / "data/outputs/run_optimized")
    )

    # modo debug
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    # executar pipeline
    run_optimized(
        base=Path(args.base),
        out=Path(args.out),
        debug=args.debug
    )