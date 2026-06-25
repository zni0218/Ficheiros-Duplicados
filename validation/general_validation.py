"""
general_validation.py

Validação de ficheiros antes do pipeline

- deteta ficheiros corrompidos
- valida extensão vs conteúdo
- garante qualidade do dataset
"""

# IMPORTS

from pathlib import Path
import csv
import time

from zipfile import ZipFile, BadZipFile

from utils.file_utils import iter_files, guess_mime, EXT_BY_CATEGORY
from utils.path_utils import path_for_csv
from utils.path_utils_safe import safe_path

from PyPDF2 import PdfReader
from PIL import Image
import soundfile as sf
import cv2
import json


# DEBUG

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# VALIDADORES

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
            pass
        return ""
    except Exception as e:
        return f"AUDIO_CORRUPT: {e}"


def check_video(path: Path) -> str:
    try:
        cap = cv2.VideoCapture(safe_path(path))

        # verificar abertura
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


# CATEGORY HELPERS

def get_category_from_ext(ext: str):
    for cat, exts in EXT_BY_CATEGORY.items():
        if ext in exts:
            return cat
    return None


def get_category_from_mime(mime: str):

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


# EXT vs MIME

def check_ext_mime_mismatch(path: Path, mime: str) -> str:

    ext = path.suffix.lower()
    category = get_category_from_ext(ext)

    if not category:
        return ""

    if category == "image" and not mime.startswith("image/"):
        return "EXT_MIME_MISMATCH(image)"

    if category == "audio" and not mime.startswith("audio/"):
        return "EXT_MIME_MISMATCH(audio)"

    if category == "video" and not mime.startswith("video/"):
        return "EXT_MIME_MISMATCH(video)"

    if ext == ".json":
        return ""

    return ""


# VALIDATOR SELECTOR

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


# MAIN

def run(base: Path, out: Path, debug: bool = False) -> dict:

    # normalizar paths
    base = Path(safe_path(base))
    out = Path(safe_path(out))

    # criar output
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "general_validation.csv"

    valid_files = []
    invalid_files = []
    rows = []

    # iterar ficheiros
    for fp in iter_files(base):

        start = time.perf_counter()

        result = "VALID"
        message = "-"
        mime = "application/octet-stream"

        # MIME

        try:
            mime = guess_mime(fp)
        except Exception:
            result = "INVALID"
            message = "MIME_ERROR"

        # EXT vs MIME

        if result == "VALID":
            mismatch = check_ext_mime_mismatch(fp, mime)
            if mismatch:
                result = "INVALID"
                message = mismatch

        # VALIDADORES

        if result == "VALID":

            # JSON tratado diretamente
            if fp.suffix.lower() == ".json":
                msg = check_json(fp)

                if msg:
                    result = "INVALID"
                    message = msg

            else:
                validator = get_validator(mime)

                # validação específica
                if validator:
                    msg = validator(fp)

                    if msg:
                        result = "INVALID"
                        message = msg

                # fallback para texto
                elif mime.startswith("text/"):
                    try:
                        with open(safe_path(fp), "r", encoding="utf-8", errors="ignore") as f:
                            f.read()
                    except Exception:
                        result = "INVALID"
                        message = "TEXT_CORRUPT"

                # tipo não suportado
                else:
                    result = "INVALID"
                    message = f"UNSUPPORTED_TYPE: {mime}"

        # tempo por ficheiro (ms)
        elapsed = round((time.perf_counter() - start) * 1000, 6)

        # categorias
        ext = fp.suffix.lower()
        ext_cat = get_category_from_ext(ext)
        mime_cat = get_category_from_mime(mime)

        # guardar resultado
        (valid_files if result == "VALID" else invalid_files).append(fp)

        rows.append({
            "method": "general",
            "validation_time_ms": elapsed,
            "mime": mime,
            "message": message,
            "result": result,
            "path": path_for_csv(fp, base, dataset_label_root=base),
            "ext_category": ext_cat,
            "mime_category": mime_cat,
            "ext_mime_match": ext_cat == mime_cat,
        })

    # CSV

    with open(safe_path(csv_path), "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(f, fieldnames=[
            "method",
            "validation_time_ms",
            "mime",
            "message",
            "result",
            "path",
            "ext_category",
            "mime_category",
            "ext_mime_match",
        ])

        writer.writeheader()
        writer.writerows(rows)

    # return final
    return {
        "valid_files": valid_files,
        "invalid_files": invalid_files,
    }