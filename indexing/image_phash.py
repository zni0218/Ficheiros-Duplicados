"""
indexing/image_phash.py

✅ geração de pHash de imagens
✅ usado no build_index
"""

from pathlib import Path
import time

from PIL import Image
import imagehash

from utils.file_utils import IMAGE_EXT


# ============================================================
# DEBUG
# ============================================================

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# ============================================================
# INDEXAÇÃO
# ============================================================

def compute_index_image_phash(files: list[Path], debug: bool = False):

    debug_print(debug, "Index image_phash")

    index = []

    for fp in files:

        if fp.suffix.lower() not in IMAGE_EXT:
            continue

        start = time.perf_counter()

        try:
            with Image.open(fp) as im:
                ph = imagehash.phash(im)
        except Exception:
            continue  # ✅ temp-friendly

        elapsed = max(0.000001, round((time.perf_counter() - start) * 1000, 6))

        index.append({
            "file_path": fp,
            "method": "image_phash",
            "fingerprint": str(ph),
            "execution_time_ms": elapsed,
        })

    return index