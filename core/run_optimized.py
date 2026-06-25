"""
run_optimized.py

Pipeline otimizado:

Usa apenas métodos selecionados para melhor performance
"""

# IMPORTS BASE

import argparse
import csv
import time

# manipulação de paths
from pathlib import Path

# normalização de paths
from utils.path_utils_safe import safe_path

# módulos do pipeline
from core.run_validation import run_validation
from core.build_index import build_index
from core.run_detection import run_detection


# MÉTODOS OTIMIZADOS

# subconjunto escolhido para reduzir custo do index
METHODS = [
    "hashing_exato",
    "tlsh",
    "image_phash",
    "text_simhash",
    "audio_phash",
    "video_phash",
]


# CSV

def write_csv(path: Path, rows):

    # não escreve se vazio
    if not rows:
        return

    # cria ficheiro novo
    with open(safe_path(path), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())

        # header
        writer.writeheader()

        # dados
        writer.writerows(rows)


# MAIN

def run_optimized(base: Path, out: Path, debug=False):

    # normaliza paths
    base = Path(safe_path(base))
    out = Path(safe_path(out))

    # cria diretoria base
    out.mkdir(parents=True, exist_ok=True)

    # estrutura de pastas
    idx_dir = out / "dataset_index"
    res_dir = out / "results"
    perf_dir = out / "performance"

    # cria se não existir
    for d in [idx_dir, res_dir, perf_dir]:
        d.mkdir(exist_ok=True)

    # timer global
    pipeline_start = time.perf_counter()

    # VALIDATION

    t0 = time.perf_counter()

    # valida ficheiros
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

    if not valid_files:
        print("[ERROR] Nenhum ficheiro válido")
        return

    # BUILD INDEX

    t0 = time.perf_counter()

    # cria fingerprints
    index_info = build_index(
        base=base,
        out=out,
        methods=METHODS,
        debug=debug
    )

    # tempo total de index
    t_index = time.perf_counter() - t0

    # tempos por método (já em segundos)
    index_times = index_info.get("method_times", {})

    # DETECTION

    t0 = time.perf_counter()

    # executa comparação
    results = run_detection(
        index_dir=out,
        temp_dir=None,
        methods=METHODS,
        debug=debug
    )

    # tempo detection
    t_detection = time.perf_counter() - t0

    # ORGANIZAR RESULTADOS

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

        m = r["method"]

        # agrupar por método
        per_method.setdefault(m, []).append(row)

        # classificação
        if r["is_exact_duplicate"]:
            exact_rows.append(row)

        elif r.get("is_strong_near_duplicate", False):
            strong_rows.append(row)
            near_rows.append(row)

        elif r["is_near_duplicate"]:
            near_rows.append(row)

    # GUARDAR RESULTADOS

    # CSVs por método
    for method, rows in per_method.items():
        write_csv(res_dir / f"{method}.csv", rows)

    # CSVs globais
    write_csv(res_dir / "ALL_exact.csv", exact_rows)
    write_csv(res_dir / "ALL_near.csv", near_rows)
    write_csv(res_dir / "ALL_strong_near.csv", strong_rows)

    # CSV completo
    write_csv(res_dir / "ALL_combined.csv", results)

    # PERFORMANCE POR MÉTODO

    detection_times = {}
    method_perf = []

    # soma detection (ms)
    for r in results:
        m = r["method"]

        detection_times.setdefault(m, 0)
        detection_times[m] += r["execution_time_ms"]

    # juntar index + detection
    for m in METHODS:

        # index já está em segundos
        idx_t = index_times.get(m, 0)

        # converter ms → segundos
        det_t = detection_times.get(m, 0) / 1000

        method_perf.append({
            "method": m,
            "index_time_s": round(idx_t, 4),
            "detection_time_s": round(det_t, 4),
            "total_time_s": round(idx_t + det_t, 4)
        })

    # guardar performance por método
    write_csv(perf_dir / "performance_methods.csv", method_perf)

    # PERFORMANCE GLOBAL

    total_time = time.perf_counter() - pipeline_start

    write_csv(
        perf_dir / "performance_global.csv",
        [{
            # tempo total pipeline
            "total_pipeline_time_s": round(total_time, 4),

            # tempos por fase
            "validation_s": round(t_validation, 4),
            "index_s": round(t_index, 4),
            "detection_s": round(t_detection, 4),

            # nº ficheiros válidos
            "total_files": len(valid_files)
        }]
    )

    print(f"[OK] Optimized pipeline em {total_time:.4f}s")


# CLI

if __name__ == "__main__":

    # raiz do projeto
    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser()

    # input
    parser.add_argument(
        "--base",
        default=str(PROJECT_ROOT / "data/original_files")
    )

    # output
    parser.add_argument(
        "--out",
        default=str(PROJECT_ROOT / "data/outputs/run_optimized")
    )

    # debug
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    # executar pipeline
    run_optimized(
        base=Path(args.base),
        out=Path(args.out),
        debug=args.debug
    )