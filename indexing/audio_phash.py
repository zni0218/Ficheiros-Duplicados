"""
indexing/audio_phash.py

✅ apenas geração de fingerprint (index)
"""

from pathlib import Path
import time

import numpy as np
import librosa
import imagehash
from PIL import Image

from utils.file_utils import AUDIO_EXT


# ============================================================
# DEBUG
# ============================================================

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# ============================================================
# ÁUDIO → ESPECTROGRAMA
# ============================================================

def audio_to_melspectrogram_image(path: Path):

    y, sr = librosa.load(path, mono=True)

    S = librosa.feature.melspectrogram(y=y, sr=sr)
    S_db = librosa.power_to_db(S, ref=np.max)

    denom = (S_db.max() - S_db.min())

    if denom == 0:
        S_norm = np.zeros_like(S_db, dtype=np.uint8)
    else:
        S_norm = (255 * (S_db - S_db.min()) / denom).astype(np.uint8)

    return Image.fromarray(S_norm)


def audio_phash(path: Path):
    img = audio_to_melspectrogram_image(path)
    return imagehash.phash(img)


# ============================================================
# INDEXAÇÃO
# ============================================================

def compute_index_audio_phash(files: list[Path], debug: bool = False):

    debug_print(debug, "Index audio_phash")

    index = []

    for fp in files:

        if fp.suffix.lower() not in AUDIO_EXT:
            continue

        start = time.perf_counter()

        try:
            ph = audio_phash(fp)
        except Exception:
            continue

        elapsed = max(0.000001, round((time.perf_counter() - start) * 1000, 6))

        index.append({
            "file_path": fp,
            "method": "audio_phash",
            "fingerprint": str(ph),
            "execution_time_ms": elapsed,
        })

    return index
