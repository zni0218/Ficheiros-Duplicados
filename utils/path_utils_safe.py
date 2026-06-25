"""
path_utils_safe.py

Utilitários para paths seguros e consistentes

- Unicode safe
- compatível Windows / Linux
- evita duplicação de paths
"""

# IMPORTS

from pathlib import Path
import unicodedata


# STRING PATH NORMALIZATION

def safe_path(p) -> str:
    """
    Normaliza path para string consistente.
    """

    # valida input
    if p is None:
        raise ValueError("safe_path recebeu None")

    # converter para Path
    path_obj = Path(p)

    try:
        # resolver caminho absoluto
        path_obj = path_obj.resolve()

    except Exception:
        # fallback (caso não exista)
        path_obj = path_obj.absolute()

    # converter para string
    path_str = str(path_obj)

    # normalizar Unicode (importante em Windows)
    path_str = unicodedata.normalize("NFC", path_str)

    # normalizar case (Windows não é case-sensitive)
    path_str = path_str.lower()

    return path_str


# PATH OBJECT NORMALIZATION

def safe_path_obj(p) -> Path:
    """
    Retorna Path normalizado.
    """

    return Path(safe_path(p))
