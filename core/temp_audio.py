"""
build_index_temp_audio.py

Teste simples de indexação para audio_phash.

✅ apenas audio_phash
✅ sem validação complexa
✅ gera CSV simples
"""

from pathlib import Path
import csv

from utils.path_utils import path_for_csv
from utils.path_utils_safe import safe_path, safe_path_obj

# ✅ IMPORT DO INDEXING CORRETO
from indexing.audio_phash import compute_index_audio_phash


# ============================================================
# MAIN
# ============================================================

def build_audio_index(base: Path, out: Path, debug=False):

    base = safe_path_obj(base)
    out = safe_path_obj(out)

    out.mkdir(parents=True, exist_ok=True)

    csv_path = out / "audio_phash_test_index.csv"

    # ========================================================
    # FICHEIROS (suporta ficheiro ou pasta)
    # ========================================================

    if base.is_file():
        files = [base]
        base_dir = base.parent
    else:
        files = list(base.rglob("*.*"))
        base_dir = base

    if debug:
        print(f"[DEBUG] ficheiros encontrados: {len(files)}")

    # ========================================================
    # INDEXAÇÃO
    # ========================================================

    raw_index = compute_index_audio_phash(files, debug=debug)

    if not raw_index:
        print("[ERROR] Nenhum áudio indexado")
        return

    # ========================================================
    # NORMALIZAÇÃO
    # ========================================================

    label_root = Path("data") / base_dir.name

    rows = []

    for r in raw_index:

        try:
            fp = r["file_path"]

            rows.append({
                "method": "audio_phash",
                "path": path_for_csv(
                    fp,
                    base_dir,
                    dataset_label_root=label_root
                ),
                "fingerprint": r["fingerprint"],
                "execution_time_ms": r.get("execution_time_ms", 0),
                "abs_path": safe_path(fp),
            })

        except Exception as e:
            if debug:
                print(f"[DEBUG] erro normalização: {e}")
            continue

    # ========================================================
    # CSV
    # ========================================================

    with open(safe_path(csv_path), "w", newline="", encoding="utf-8") as f:

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

        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] CSV gerado: {csv_path}")
    print(f"[INFO] Linhas: {len(rows)}")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    import argparse

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    default_base = PROJECT_ROOT / "data/original_files/audio"

    parser = argparse.ArgumentParser(
        description="Teste audio_phash index"
    )

    parser.add_argument("--base", default=str(default_base))
    parser.add_argument("--out", default=str(PROJECT_ROOT / "data/outputs/test"))
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    build_audio_index(
        base=Path(args.base),
        out=Path(args.out),
        debug=args.debug
    )
