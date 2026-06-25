"""
audio_phash.py

Geração de fingerprint perceptual para áudio

- converte áudio em espectrograma
- aplica perceptual hash (phash)
"""

from pathlib import Path
import time

import numpy as np
import librosa
import imagehash
from PIL import Image

from utils.file_utils import AUDIO_EXT


# DEBUG

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# ÁUDIO → ESPECTROGRAMA

def audio_to_melspectrogram_image(path: Path):
    """
    Converte áudio para imagem (mel-spectrogram).
    """

    y, sr = librosa.load(path, mono=True)

    # espectrograma
    S = librosa.feature.melspectrogram(y=y, sr=sr)

    # escala log
    S_db = librosa.power_to_db(S, ref=np.max)

    denom = (S_db.max() - S_db.min())

    # normalização para imagem
    if denom == 0:
        S_norm = np.zeros_like(S_db, dtype=np.uint8)
    else:
        S_norm = (255 * (S_db - S_db.min()) / denom).astype(np.uint8)

    return Image.fromarray(S_norm)


def audio_phash(path: Path):
    """
    Calcula perceptual hash do áudio.
    """

    img = audio_to_melspectrogram_image(path)
    return imagehash.phash(img)


# INDEXAÇÃO

def compute_index_audio_phash(files: list[Path], debug: bool = False):
    """
    Gera fingerprints audio_phash para um conjunto de ficheiros.
    """

    debug_print(debug, "Index audio_phash")

    index = []

    for fp in files:

        # filtrar apenas áudio
        if fp.suffix.lower() not in AUDIO_EXT:
            continue

        start = time.perf_counter()

        try:
            ph = audio_phash(fp)
        except Exception:
            continue

        # tempo por ficheiro (ms)
        elapsed = max(0.000001, round((time.perf_counter() - start) * 1000, 6))

        index.append({
            "file_path": fp,
            "method": "audio_phash",
            "fingerprint": str(ph),
            "execution_time_ms": elapsed,
        })

    return index