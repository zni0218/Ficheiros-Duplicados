"""
build_index.py

Indexação multi-método.

✅ dataset + temp (temp_mode)
✅ CSV por método
✅ combined_index (dataset)
✅ append no temp
✅ path curto + abs_path
"""

from pathlib import Path
import argparse
import csv
import time

from core.run_validation import run_validation

from utils.path_utils import path_for_csv
from utils.file_utils import guess_mime
from utils.path_utils_safe import safe_path, safe_path_obj


# ============================================================
# IMPORTS (INDEXING)
# ============================================================

import indexing.hashing_exato as hashing_exato
import indexing.fuzzy_chunks as fuzzy_chunks
import indexing.image_phash as image_phash
import indexing.audio_phash as audio_phash
import indexing.text_simhash as text_simhash
import indexing.video_phash as video_phash
import indexing.ssdeep_hash as ssdeep_hash
import indexing.tlsh_hash as tlsh_hash


# ============================================================
# METHODS
# ============================================================

INDEX_METHODS = {
    "hashing_exato": getattr(hashing_exato, "compute_index_hashing_exato", None),
    "fuzzy_chunks": getattr(fuzzy_chunks, "compute_index_fuzzy_chunks", None),
    "image_phash": getattr(image_phash, "compute_index_image_phash", None),
    "audio_phash": getattr(audio_phash, "compute_index_audio_phash", None),
    "text_simhash": getattr(text_simhash, "compute_index_text_simhash", None),
    "video_phash": getattr(video_phash, "compute_index_video_phash", None),
    "ssdeep": getattr(ssdeep_hash, "compute_index_ssdeep", None),
    "tlsh": getattr(tlsh_hash, "compute_index_tlsh", None),
}


# ============================================================
# DEBUG
# ============================================================

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# ============================================================
# FILTER MIME
# ============================================================

def filter_files(files, method):

    filtered = []

    for fp in files:
        try:
            mime = guess_mime(fp)

            if method == "image_phash":
                if mime.startswith("image/"):
                    filtered.append(fp)

            elif method == "audio_phash":
                if mime.startswith("audio/"):
                    filtered.append(fp)

            elif method == "video_phash":
                if mime.startswith("video/"):
                    filtered.append(fp)

            elif method == "text_simhash":
                if mime.startswith("text/") or "json" in mime:
                    filtered.append(fp)

            else:
                filtered.append(fp)

        except:
            continue

    return filtered


# ============================================================
# CSV WRITERS
# ============================================================

def write_csv(path: Path, rows: list[dict], append=False):

    exists = path.exists()
    mode = "a" if append else "w"

    with open(safe_path(path), mode, newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "method",
                "path",
                "fingerprint",
                "execution_time_ms",
                "abs_path",
            ],
        )

        if not exists or not append:
            writer.writeheader()

        writer.writerows(rows)


def write_combined_csv(path: Path, rows: list[dict]):

    if not rows:
        return

    keys = set()
    for r in rows:
        keys.update(r.keys())

    method_cols = sorted(
        k for k in keys if k not in ("path", "abs_path")
    )

    fieldnames = ["path"] + method_cols + ["abs_path"]

    with open(safe_path(path), "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# MERGE
# ============================================================

def merge_indexes(all_rows: dict):

    combined = {}

    for method, rows in all_rows.items():

        for r in rows:

            key = r["path"]

            if key not in combined:
                combined[key] = {
                    "path": r["path"],
                    "abs_path": r["abs_path"],
                }

            combined[key][method] = r["fingerprint"]

    return list(combined.values())


# ============================================================
# MAIN
# ============================================================

def build_index(
    base: Path,
    out: Path,
    debug: bool = False,
    temp_mode: bool = False
):

    base = safe_path_obj(base)
    out = safe_path_obj(out)

    index_dir = out / ("temp_index" if temp_mode else "dataset_index")
    index_dir.mkdir(parents=True, exist_ok=True)

    # ✅ ficheiro ou pasta
    if base.is_file():
        files = [base]
        base_dir = base.parent
    else:
        files = list(base.rglob("*.*"))
        base_dir = base

    label_root = Path("data") / base_dir.name

    # --------------------------------------------------------
    # VALIDATION (só dataset)
    # --------------------------------------------------------

    if not temp_mode:

        debug_print(debug, "Running validation")

        validation = run_validation(
            base=base,
            out=out / "validation",
            debug=debug,
            temp_mode=False
        )

        files = validation["valid_files"]

        if not files:
            print("[ERROR] Nenhum ficheiro válido")
            return

    # --------------------------------------------------------
    # INDEX
    # --------------------------------------------------------

    all_method_rows = {}

    for method, fn in INDEX_METHODS.items():

        if fn is None:
            continue

        method_files = filter_files(files, method)

        if not method_files:
            continue

        try:
            raw = fn(method_files, debug=debug)
        except:
            continue

        rows = []

        for r in raw:
            try:
                fp = r["file_path"]

                rows.append({
                    "method": method,
                    "path": path_for_csv(
                        fp,
                        base_dir,
                        dataset_label_root=label_root
                    ),
                    "fingerprint": r["fingerprint"],
                    "execution_time_ms": r.get("execution_time_ms", 0),
                    "abs_path": safe_path(fp),
                })

            except:
                continue

        if not rows:
            continue

        csv_path = index_dir / (
            f"{method}_temp_index.csv" if temp_mode
            else f"{method}_index.csv"
        )

        write_csv(csv_path, rows, append=temp_mode)

        if not temp_mode:
            all_method_rows[method] = rows

        if debug:
            print(f"[{method}] {len(rows)} entries")

    # --------------------------------------------------------
    # COMBINED (SÓ DATASET)
    # --------------------------------------------------------

    if not temp_mode:

        combined = merge_indexes(all_method_rows)

        write_combined_csv(
            index_dir / "combined_index.csv",
            combined
        )

        if debug:
            print(f"[COMBINED] {len(combined)} entries")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    default_base = PROJECT_ROOT / "data/original_files"

    parser = argparse.ArgumentParser()

    parser.add_argument("--base", default=str(default_base))
    parser.add_argument("--out", default=str(PROJECT_ROOT / "data/outputs"))
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    build_index(
        base=Path(args.base),
        out=Path(args.out),
        debug=args.debug,
        temp_mode=False
    )
