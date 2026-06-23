"""
run_validation.py

Validação de ficheiros (dataset + inputs).

✅ suporta ficheiro ou pasta
✅ dataset → overwrite
✅ inputs → append (temp_mode)
✅ separação por categoria
✅ mantém general_validation.csv
✅ path curto + abs_path
"""

import argparse
import csv
import time
from pathlib import Path
from collections import defaultdict

from utils.file_utils import iter_files, guess_mime
from utils.path_utils import path_for_csv
from utils.path_utils_safe import safe_path, safe_path_obj

from validation.general_validation import (
    get_validator,
    check_ext_mime_mismatch,
    get_category_from_ext,
    get_category_from_mime
)


# ============================================================
# DEBUG
# ============================================================

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# ============================================================
# CORE
# ============================================================

def run_validation(
    base: Path,
    out: Path,
    debug: bool = False,
    temp_mode: bool = False
) -> dict:

    base = safe_path_obj(base)
    out = safe_path_obj(out)

    out.mkdir(parents=True, exist_ok=True)

    valid_files = []
    invalid_files = []
    rows = []

    # ========================================================
    # FICHEIROS (ficheiro OU pasta)
    # ========================================================

    if base.is_file():
        files = [base]
        base_dir = base.parent
    else:
        files = list(iter_files(base))
        base_dir = base

    label_root = Path("data") / base_dir.name

    # ========================================================

    for fp in files:

        start = time.perf_counter()

        result = "VALID"
        message = "-"
        mime = "application/octet-stream"

        # ---------------- MIME ----------------
        try:
            mime = guess_mime(fp)
            debug_print(debug, f"{fp} → {mime}")
        except Exception as e:
            result = "INVALID"
            message = f"MIME_ERROR: {e}"

        # ---------------- EXT vs MIME ----------------
        if result == "VALID":
            mismatch = check_ext_mime_mismatch(fp, mime)
            if mismatch:
                result = "INVALID"
                message = mismatch

        # ---------------- VALIDADORES ----------------
        if result == "VALID":

            validator = get_validator(mime)

            if validator:
                msg = validator(fp)
                if msg:
                    result = "INVALID"
                    message = msg

            elif mime.startswith("text/"):
                try:
                    with open(safe_path(fp), "r", encoding="utf-8", errors="ignore") as f:
                        f.read()
                except Exception:
                    result = "INVALID"
                    message = "TEXT_CORRUPT"

            else:
                message = f"UNSUPPORTED_TYPE: {mime}"

        # ---------------- TEMPO ----------------
        elapsed = round((time.perf_counter() - start) * 1000, 6)

        # ---------------- CATEGORIAS ----------------
        ext = fp.suffix.lower()
        ext_cat = get_category_from_ext(ext)
        mime_cat = get_category_from_mime(mime)

        # 👉 prioridade ao MIME (mais correto)
        category = mime_cat or "unknown"

        # ---------------- PATHS ----------------

        short_path = path_for_csv(
            fp,
            base_dir,
            dataset_label_root=label_root
        )

        abs_path = safe_path(fp)

        # ---------------- RESULTADOS ----------------

        if result == "VALID":
            valid_files.append(fp)
        else:
            invalid_files.append(fp)

        row = {
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
        }

        rows.append(row)

    # ========================================================
    # ✅ AGRUPAR POR CATEGORIA
    # ========================================================

    category_rows = defaultdict(list)

    for row in rows:
        cat = row["mime_category"] or "unknown"
        category_rows[cat].append(row)

    # ========================================================
    # ✅ WRITE POR CATEGORIA
    # ========================================================

    for category, cat_rows in category_rows.items():

        if temp_mode:
            csv_path = out / f"temp_{category}_validation.csv"
        else:
            csv_path = out / f"{category}_validation.csv"

        exists = csv_path.exists()
        mode = "a" if temp_mode else "w"

        with open(safe_path(csv_path), mode, newline="", encoding="utf-8") as f:

            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "method",
                    "validation_time_ms",
                    "mime",
                    "message",
                    "result",
                    "path",
                    "ext_category",
                    "mime_category",
                    "ext_mime_match",
                    "abs_path",
                ],
            )

            if not exists or not temp_mode:
                writer.writeheader()

            writer.writerows(cat_rows)

        debug_print(debug, f"[CSV] {category}: {len(cat_rows)} entradas")

    # ========================================================
    # ✅ GENERAL CSV (sempre existe)
    # ========================================================

    if temp_mode:
        csv_path = out / "temp_validation.csv"
        mode = "a"
        exists = csv_path.exists()
    else:
        csv_path = out / "general_validation.csv"
        mode = "w"
        exists = False

    with open(safe_path(csv_path), mode, newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "method",
                "validation_time_ms",
                "mime",
                "message",
                "result",
                "path",
                "ext_category",
                "mime_category",
                "ext_mime_match",
                "abs_path",
            ],
        )

        if not exists or not temp_mode:
            writer.writeheader()

        writer.writerows(rows)

    debug_print(debug, f"[CSV] general: {len(rows)} entradas")

    return {
        "valid_files": [safe_path_obj(p) for p in valid_files],
        "invalid_files": [safe_path_obj(p) for p in invalid_files],
    }


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

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

    run_validation(
        base=Path(args.base),
        out=Path(args.out),
        debug=args.debug,
        temp_mode=False
    )