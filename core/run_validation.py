"""
run_validation.py

Validação de ficheiros

"""

# IMPORTS BASE

import argparse
import csv
import time

from pathlib import Path
from collections import defaultdict

# utilitários
from utils.file_utils import iter_files, guess_mime
from utils.path_utils import path_for_csv
from utils.path_utils_safe import safe_path, safe_path_obj

# validação
from validation.general_validation import (
    get_validator,
    check_ext_mime_mismatch,
    get_category_from_ext,
    get_category_from_mime
)


# MAIN

def run_validation(base: Path, out: Path, debug=False, temp_mode=False):

    # normaliza paths
    base = safe_path_obj(base)
    out = safe_path_obj(out)

    # cria pasta output
    out.mkdir(parents=True, exist_ok=True)

    valid_files = []
    invalid_files = []
    rows = []

    # FILES

    if base.is_file():
        # apenas um ficheiro
        files = [base]
        base_dir = base.parent
    else:
        # diretoria completa
        files = list(iter_files(base))
        base_dir = base

    # VALIDATION LOOP

    for fp in files:

        start = time.perf_counter()

        result = "VALID"
        message = "-"
        mime = "application/octet-stream"

        # MIME

        try:
            mime = guess_mime(fp)
        except Exception as e:
            result = "INVALID"
            message = f"MIME_ERROR: {e}"

        # EXT vs MIME

        if result == "VALID":
            mismatch = check_ext_mime_mismatch(fp, mime)

            if mismatch:
                result = "INVALID"
                message = mismatch

        # VALIDATORS

        if result == "VALID":

            validator = get_validator(mime)

            # validação específica por tipo
            if validator:
                msg = validator(fp)

                if msg:
                    result = "INVALID"
                    message = msg

            # fallback para texto
            elif mime.startswith("text/"):
                try:
                    with open(safe_path(fp), "r", encoding="utf-8", errors="ignore") as f:
                        f.read()
                except:
                    result = "INVALID"
                    message = "TEXT_CORRUPT"

            # tipo não suportado
            else:
                message = f"UNSUPPORTED_TYPE: {mime}"

        # tempo de validação por ficheiro (ms)
        elapsed = round((time.perf_counter() - start) * 1000, 6)

        # categorias
        ext = fp.suffix.lower()
        ext_cat = get_category_from_ext(ext)
        mime_cat = get_category_from_mime(mime)

        category = mime_cat or "unknown"

        # paths
        short_path = path_for_csv(fp, base_dir)
        abs_path = safe_path(fp)

        # separar válidos / inválidos
        if result == "VALID":
            valid_files.append(fp)
        else:
            invalid_files.append(fp)

        # guardar linha
        rows.append({
            "method": "general",
            "validation_time_ms": elapsed,
            "mime": mime,
            "message": message,
            "result": result,
            "path": short_path,
            "ext_category": ext_cat,
            "mime_category": mime_cat,
            "ext_mime_match": (
                ext_cat == mime_cat
            ) if ext_cat and mime_cat else True,
            "abs_path": abs_path,
        })

    # GROUP BY CATEGORY

    grouped = defaultdict(list)

    for r in rows:
        cat = r["mime_category"] or "unknown"
        grouped[cat].append(r)

    # WRITE CATEGORY CSVs

    for category, cat_rows in grouped.items():

        csv_path = out / f"{category}_validation.csv"

        # dataset → w / interactive → a
        mode = "a" if temp_mode else "w"
        exists = csv_path.exists()

        with open(safe_path(csv_path), mode, newline="", encoding="utf-8") as f:

            writer = csv.DictWriter(
                f,
                fieldnames=cat_rows[0].keys()
            )

            # header
            if not exists or not temp_mode:
                writer.writeheader()

            writer.writerows(cat_rows)

    # WRITE GENERAL CSV

    general_path = out / "general_validation.csv"

    mode = "a" if temp_mode else "w"
    exists = general_path.exists()

    with open(safe_path(general_path), mode, newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys()
        )

        if not exists or not temp_mode:
            writer.writeheader()

        writer.writerows(rows)

    # return final
    return {
        "valid_files": [safe_path_obj(p) for p in valid_files],
        "invalid_files": [safe_path_obj(p) for p in invalid_files],
    }


# CLI

if __name__ == "__main__":

    # raiz do projeto
    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    # escolher base automática
    default_base = (
        PROJECT_ROOT / "data/original_files"
        if (PROJECT_ROOT / "data/original_files").exists()
        else PROJECT_ROOT / "data/inputs"
    )

    parser = argparse.ArgumentParser(description="Validação do dataset")

    parser.add_argument("--base", default=str(default_base))
    parser.add_argument("--out", default=str(PROJECT_ROOT / "data/outputs/validation"))
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    # executar validação
    run_validation(
        base=Path(args.base),
        out=Path(args.out),
        debug=args.debug,
        temp_mode=False
    )