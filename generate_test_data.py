"""
general_validation.py

Validação de ficheiros antes do pipeline de deduplicação.

✅ deteta ficheiros corrompidos
✅ valida coerência extensão vs conteúdo
✅ garante qualidade de input

⚠️ Apenas lógica — sem execução (run)
"""

# ============================================================
# IMPORTS
# ============================================================

from pathlib import Path
from zipfile import ZipFile, BadZipFile

from utils.file_utils import guess_mime, EXT_BY_CATEGORY
from utils.path_utils_safe import safe_path

from PyPDF2 import PdfReader
from PIL import Image
import soundfile as sf
import cv2
import json


# ============================================================
# VALIDADORES
# ============================================================

def check_cdfv2(path: Path) -> str:
    try:
        with open(safe_path(path), "rb") as f:
            header = f.read(8)

        if header != b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
            return "CDFV2_INVALID_HEADER"

        return ""
    except Exception as e:
        return f"CDFV2_ERROR: {e}"


def check_pdf(path: Path) -> str:
    try:
        PdfReader(safe_path(path))
        return ""
    except Exception as e:
        return f"PDF_CORRUPT: {e}"


def check_zip(path: Path) -> str:
    try:
        with ZipFile(safe_path(path)) as z:
            z.namelist()
        return ""
    except BadZipFile as e:
        return f"ZIP_CORRUPT: {e}"
    except Exception as e:
        return f"ZIP_ERROR: {e}"


def check_image(path: Path) -> str:
    try:
        with Image.open(safe_path(path)) as img:
            img.verify()
        return ""
    except Exception as e:
        return f"IMAGE_CORRUPT: {e}"


def check_audio(path: Path) -> str:
    try:
        with sf.SoundFile(safe_path(path)):
            return ""
    except Exception as e:
        return f"AUDIO_CORRUPT: {e}"


def check_video(path: Path) -> str:
    try:
        cap = cv2.VideoCapture(safe_path(path))

        if not cap.isOpened():
            cap.release()
            return "VIDEO_CORRUPT"

        ok, _ = cap.read()
        cap.release()

        if not ok:
            return "VIDEO_CORRUPT"

        return ""
    except Exception as e:
        return f"VIDEO_CORRUPT: {e}"


def check_json(path: Path) -> str:
    try:
        with open(safe_path(path), "r", encoding="utf-8", errors="ignore") as f:
            json.load(f)
        return ""
    except Exception as e:
        return f"JSON_CORRUPT: {e}"


# ============================================================
# CATEGORIAS
# ============================================================

def get_category_from_ext(ext: str):
    if not ext:
        return None

    ext = ext.lower()

    for cat, exts in EXT_BY_CATEGORY.items():
        if ext in exts:
            return cat

    return None


def get_category_from_mime(mime: str):
    if not mime:
        return None

    if mime.startswith("image/"):
        return "image"

    if mime.startswith("audio/"):
        return "audio"

    if mime.startswith("video/"):
        return "video"

    if mime.startswith("text/"):
        return "text"

    if mime == "application/json":
        return "text"

    if "zip" in mime:
        return "archive"

    if mime.startswith("application/CDFV2") or mime.startswith("application/pdf"):
        return "document"

    return None


# ============================================================
# EXT vs MIME
# ============================================================

def check_ext_mime_mismatch(path: Path, mime: str) -> str:
    ext = path.suffix.lower()

    ext_cat = get_category_from_ext(ext)
    mime_cat = get_category_from_mime(mime)

    if not ext_cat or not mime_cat:
        return ""

    if ext_cat != mime_cat:
        return f"EXT_MIME_MISMATCH({ext_cat} vs {mime_cat})"

    return ""


# ============================================================
# VALIDATOR SELECTOR
# ============================================================

def get_validator(mime: str):

    if mime.startswith("application/CDFV2"):
        return check_cdfv2

    if mime.startswith("application/pdf"):
        return check_pdf

    if "zip" in mime:
        return check_zip

    if mime.startswith("image/"):
        return check_image

    if mime.startswith("audio/"):
        return check_audio

    if mime.startswith("video/"):
        return check_video

    if mime == "application/json":
        return check_json

    return None