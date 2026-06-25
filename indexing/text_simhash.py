"""
text_simhash.py

Geração de fingerprint SimHash para texto

- converte texto em hash binário (similaridade)
- robusto a pequenas alterações
"""

from pathlib import Path
import time

from simhash import Simhash
from utils.file_utils import TEXT_EXT


# DEBUG

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# LEITURA SEGURA

def read_text_safe(path: Path) -> str:
    """
    Lê ficheiro de texto com fallback de encoding.
    """

    # tentar múltiplos encodings
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue

    return ""


# INDEXAÇÃO

def compute_index_text_simhash(files: list[Path], debug=False):
    """
    Gera fingerprints SimHash para ficheiros de texto.
    """

    debug_print(debug, "Index text_simhash")

    index = []

    for fp in files:

        # filtrar apenas texto
        if fp.suffix.lower() not in TEXT_EXT:
            continue

        start = time.perf_counter()

        # leitura segura
        text = read_text_safe(fp)

        # ignorar texto vazio
        if not text.strip():
            continue

        try:
            # calcular SimHash
            sh = Simhash(text)

            # garantir valor válido
            assert sh.value is not None

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
            "method": "text_simhash",
            "fingerprint": str(int(sh.value)),  # guardar como string
            "execution_time_ms": elapsed,
        })

    return index