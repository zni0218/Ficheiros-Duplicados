"""
image_phash.py

Geração de fingerprint perceptual para imagens

- usa perceptual hash (pHash)
- robusto a pequenas alterações visuais
"""

from pathlib import Path
import time

from PIL import Image
import imagehash

from utils.file_utils import IMAGE_EXT


# DEBUG

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# INDEXAÇÃO

def compute_index_image_phash(files: list[Path], debug: bool = False):
    """
    Gera pHash para ficheiros de imagem.
    """

    debug_print(debug, "Index image_phash")

    index = []

    for fp in files:

        # filtrar apenas imagens
        if fp.suffix.lower() not in IMAGE_EXT:
            continue

        start = time.perf_counter()

        try:
            # calcular perceptual hash
            with Image.open(fp) as im:
                ph = imagehash.phash(im)

        except Exception:
            # ignorar ficheiros problemáticos
            continue

        # tempo por ficheiro (ms)
        elapsed = max(
            0.000001,
            round((time.perf_counter() - start) * 1000, 6)
        )

        index.append({
            "file_path": fp,
            "method": "image_phash",
            "fingerprint": str(ph),
            "execution_time_ms": elapsed,
        })

    return index