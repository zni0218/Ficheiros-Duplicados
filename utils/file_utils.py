"""
file_utils.py

LOW-LEVEL utilities para:
- Hashing
- MIME detection
- Iteração de ficheiros

✅ Sem lógica de negócio
✅ Seguro para Windows / Unicode
"""

# ============================================================
# IMPORTS
# ============================================================

from pathlib import Path
import hashlib
from typing import Iterable, Optional
import mimetypes
import magic

from utils.path_utils_safe import safe_path


# ============================================================
# CONFIG
# ============================================================

BUFFER_SIZE = 1024 * 1024  # 1MB leitura eficiente

# ✅ Manter uma única instância
_MAGIC = magic.Magic(mime=True)


# ============================================================
# EXTENSIONS (NECESSÁRIO PARA VALIDATION)
# ============================================================

"""
⚠️ IMPORTANTE:

Estas listas NÃO garantem o tipo real.

Servem para:
✅ categorização inicial
✅ validações cruzadas (EXT vs MIME)
✅ fallback quando MIME falha
"""

EXT_BY_CATEGORY = {
    "text": {
        ".txt", ".md", ".log",
        ".json", ".csv", ".xml",
        ".yaml", ".yml",
        ".ini", ".cfg"
    },
    "document": {
        ".pdf", ".doc", ".docx",
        ".xls", ".xlsx",
        ".ppt", ".pptx",
        ".rtf"
    },
    "image": {
        ".png", ".jpg", ".jpeg",
        ".tif", ".tiff",
        ".bmp", ".gif", ".webp"
    },
    "audio": {
        ".mp3", ".wav", ".flac",
        ".ogg", ".m4a", ".aac"
    },
    "video": {
        ".mp4", ".mkv", ".avi",
        ".mov", ".wmv", ".webm"
    },
    "archive": {
        ".zip", ".rar", ".7z",
        ".tar", ".gz", ".bz2"
    },
    "binary": {
        ".exe", ".dll", ".bin",
        ".dat", ".iso"
    },
}

# ✅ atalhos (melhor legibilidade noutros módulos)
TEXT_EXT     = EXT_BY_CATEGORY["text"]
DOCUMENT_EXT = EXT_BY_CATEGORY["document"]
IMAGE_EXT    = EXT_BY_CATEGORY["image"]
AUDIO_EXT    = EXT_BY_CATEGORY["audio"]
VIDEO_EXT    = EXT_BY_CATEGORY["video"]
ARCHIVE_EXT  = EXT_BY_CATEGORY["archive"]
BINARY_EXT   = EXT_BY_CATEGORY["binary"]

# ============================================================
# MIME DETECTION
# ============================================================

def guess_mime(path: Path, debug: bool = False) -> str:
    """
    Determina MIME real de forma robusta e segura para Unicode (Windows).
    """

    path_str = safe_path(path)

    # ✅ MÉTODO PRINCIPAL (SEMPRE PRIORIDADE)
    try:
        with open(path_str, "rb") as f:
            header = f.read(8192)
            if header:
                return _MAGIC.from_buffer(header)
    except Exception as e:
        if debug:
            print(f"[DEBUG] from_buffer falhou: {path_str} | {e}")

    # ❌ NÃO confiar em from_file no Windows
    # (só usar como fallback opcional, não crítico)

    # ✅ fallback extensão
    mime, _ = mimetypes.guess_type(path_str)
    if mime:
        return mime

    # ✅ fallback final seguro
    return "application/octet-stream"

# ============================================================
# ITER FILES
# ============================================================

def iter_files(base: Path, exts: Optional[Iterable[str]] = None):
    """
    Itera ficheiros de forma segura.
    """

    base = Path(safe_path(base))
    exts = {e.lower() for e in exts} if exts else None

    IGNORED = {".DS_Store", "Thumbs.db"}

    for p in base.rglob("*"):
        try:
            if not p.is_file():
                continue

            if p.name in IGNORED:
                continue

            if exts is None or p.suffix.lower() in exts:
                yield p

        except Exception:
            continue


# ============================================================
# SHA-256
# ============================================================

def sha256_file(path: Path) -> str:
    """
    Hash SHA-256 eficiente.
    """

    path_str = safe_path(path)
    h = hashlib.sha256()

    with open(path_str, "rb") as f:
        for chunk in iter(lambda: f.read(BUFFER_SIZE), b""):
            h.update(chunk)

    return h.hexdigest()


# ============================================================
# CHUNK HASHING
# ============================================================

def chunk_hashes(path: Path, chunk_size: int = 65536) -> list[str]:
    """
    Hash por blocos (fuzzy).
    """

    path_str = safe_path(path)
    hashes = []

    MAX_CHUNKS = 10000

    with open(path_str, "rb") as f:
        count = 0

        for chunk in iter(lambda: f.read(chunk_size), b""):
            hashes.append(hashlib.sha256(chunk).hexdigest())

            count += 1
            if count >= MAX_CHUNKS:
                break

    return hashes