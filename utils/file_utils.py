"""
file_utils.py

Utilitários base para:
- hashing
- deteção de MIME
- iteração de ficheiros

"""

# IMPORTS

from pathlib import Path
import hashlib
from typing import Iterable, Optional
import mimetypes
import magic

# utilitário de path seguro
from utils.path_utils_safe import safe_path


# CONFIG

# tamanho de buffer para leitura eficiente
BUFFER_SIZE = 1024 * 1024  # 1MB

# instância global do magic (mais eficiente)
_MAGIC = magic.Magic(mime=True)


# EXTENSIONS

# listas usadas para categorização e validação
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

# atalhos para outros módulos
TEXT_EXT     = EXT_BY_CATEGORY["text"]
DOCUMENT_EXT = EXT_BY_CATEGORY["document"]
IMAGE_EXT    = EXT_BY_CATEGORY["image"]
AUDIO_EXT    = EXT_BY_CATEGORY["audio"]
VIDEO_EXT    = EXT_BY_CATEGORY["video"]
ARCHIVE_EXT  = EXT_BY_CATEGORY["archive"]
BINARY_EXT   = EXT_BY_CATEGORY["binary"]


# MIME DETECTION

def guess_mime(path: Path, debug: bool = False) -> str:
    """
    Detecta MIME real com fallback seguro.
    """

    path_str = safe_path(path)

    # tentativa principal (header)
    try:
        with open(path_str, "rb") as f:
            header = f.read(8192)

            if header:
                return _MAGIC.from_buffer(header)

    except Exception as e:
        if debug:
            print(f"[DEBUG] from_buffer falhou: {path_str} | {e}")

    # fallback por extensão
    mime, _ = mimetypes.guess_type(path_str)

    if mime:
        return mime

    # fallback final
    return "application/octet-stream"


# ITER FILES

def iter_files(base: Path, exts: Optional[Iterable[str]] = None):
    """
    Itera ficheiros válidos de forma segura.
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


# SHA-256

def sha256_file(path: Path) -> str:
    """
    Calcula hash SHA-256 do ficheiro.
    """

    path_str = safe_path(path)
    h = hashlib.sha256()

    with open(path_str, "rb") as f:
        for chunk in iter(lambda: f.read(BUFFER_SIZE), b""):
            h.update(chunk)

    return h.hexdigest()


# CHUNK HASHING

def chunk_hashes(path: Path, chunk_size: int = 8192) -> list[str]:
    """
    Gera hashes por blocos (fuzzy).
    """

    path_str = safe_path(path)
    hashes = []

    MAX_CHUNKS = 300

    with open(path_str, "rb") as f:

        count = 0

        for chunk in iter(lambda: f.read(chunk_size), b""):

            hashes.append(hashlib.sha256(chunk).hexdigest())

            count += 1
            if count >= MAX_CHUNKS:
                break

    return hashes