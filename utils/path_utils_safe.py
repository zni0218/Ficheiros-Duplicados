"""
path_utils_safe.py

Utilitários para paths seguros e consistentes.

✅ Unicode safe
✅ Windows / Linux
✅ Evita duplicação de paths
"""

# ============================================================
# IMPORTS
# ============================================================

from pathlib import Path
import unicodedata


# ============================================================
# STRING PATH NORMALIZATION
# ============================================================

def safe_path(p) -> str:
    """
    Normaliza path para string segura e consistente.

    ✅ Unicode (NFC)
    ✅ resolve caminhos relativos
    ✅ normaliza case (Windows-safe)
    """

    if p is None:
        raise ValueError("safe_path recebeu None")

    # converter para Path primeiro
    path_obj = Path(p)

    try:
        # resolve (remove ./ ../ etc)
        path_obj = path_obj.resolve()
    except Exception:
        # fallback se path não existir
        path_obj = path_obj.absolute()

    # converter para string
    path_str = str(path_obj)

    # Unicode normalize
    path_str = unicodedata.normalize("NFC", path_str)

    # 🔴 IMPORTANTE:
    # normalize case (Windows não é case-sensitive)
    path_str = path_str.lower()

    return path_str


# ============================================================
# PATH OBJECT NORMALization
# ============================================================

def safe_path_obj(p) -> Path:
    """
    Retorna Path já normalizado.
    """

    return Path(safe_path(p))