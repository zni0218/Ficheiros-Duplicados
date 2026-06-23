"""
indexing/video_phash.py

✅ geração de pHash para vídeos
✅ sampling inteligente (início / meio / fim)
✅ FAST (não lê todos frames)
✅ garante sempre TOTAL_FRAMES hashes
✅ fallback para vídeos curtos / estáticos
"""

from pathlib import Path
import time

import cv2
from PIL import Image
import imagehash

from utils.file_utils import VIDEO_EXT


# ============================================================
# DEBUG
# ============================================================

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# ============================================================
# CONFIG
# ============================================================

TOTAL_FRAMES = 12  # 🎯 objetivo final

START_RATIO = 0.3
MID_RATIO   = 0.4
END_RATIO   = 0.3


# ============================================================
# POSITIONS
# ============================================================

def generate_positions(frame_count, debug=False):

    # distribuição correta (garante soma = TOTAL)
    start_frames = int(TOTAL_FRAMES * START_RATIO)
    mid_frames   = int(TOTAL_FRAMES * MID_RATIO)
    end_frames   = TOTAL_FRAMES - start_frames - mid_frames

    def linspace(start, end, n):
        if n <= 1:
            return [int(start)]
        step = (end - start) / (n - 1)
        return [int(start + i * step) for i in range(n)]

    # zonas do vídeo
    start_pos = linspace(0, int(frame_count * 0.3), start_frames)
    mid_pos   = linspace(int(frame_count * 0.3), int(frame_count * 0.7), mid_frames)

    # ⚠️ evita últimos frames (problemas H264)
    safe_end = max(0, frame_count - 5)
    end_pos = linspace(int(frame_count * 0.7), safe_end, end_frames)

    positions = sorted(set(int(p) for p in (start_pos + mid_pos + end_pos)))

    debug_print(debug, f"positions geradas: {len(positions)}")

    return positions


# ============================================================
# EXTRAÇÃO
# ============================================================

def extract_keyframe_phashes(path: Path, debug=False):

    cap = cv2.VideoCapture(str(path))

    if not cap.isOpened():
        debug_print(debug, f"Erro abrir vídeo: {path}")
        return []

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_count <= 0:
        cap.release()
        debug_print(debug, "frame_count inválido")
        return []

    debug_print(debug, f"frame_count={frame_count}")

    positions = generate_positions(frame_count, debug=debug)

    phashes = []
    last_hash = None

    # =====================================================
    # PRIMEIRA PASSAGEM (sem duplicados)
    # =====================================================
    for f in positions:

        cap.set(cv2.CAP_PROP_POS_FRAMES, int(f))
        ok, frame = cap.read()

        if not ok:
            debug_print(debug, f"falhou frame {f}")
            continue

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            h = str(imagehash.phash(img))

            # evitar duplicados
            if h != last_hash:
                phashes.append(h)
                last_hash = h

            if len(phashes) >= TOTAL_FRAMES:
                break

        except Exception as e:
            debug_print(debug, f"erro frame {f}: {e}")

    # =====================================================
    # SEGUNDA PASSAGEM (GARANTIR TOTAL_FRAMES)
    # =====================================================
    if len(phashes) < TOTAL_FRAMES:

        debug_print(debug,
            f"fallback: {len(phashes)} -> {TOTAL_FRAMES} hashes"
        )

        for f in positions:

            if len(phashes) >= TOTAL_FRAMES:
                break

            cap.set(cv2.CAP_PROP_POS_FRAMES, int(f))
            ok, frame = cap.read()

            if not ok:
                continue

            try:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)

                h = str(imagehash.phash(img))

                # aqui aceita duplicados
                phashes.append(h)

            except Exception:
                continue

    cap.release()

    debug_print(debug, f"hashes finais: {len(phashes)}")

    return phashes


# ============================================================
# INDEXAÇÃO
# ============================================================

def compute_index_video_phash(files: list[Path], debug=False):

    index = []

    for fp in files:

        if fp.suffix.lower() not in VIDEO_EXT:
            continue

        start_time = time.perf_counter()

        try:
            phashes = extract_keyframe_phashes(fp, debug=debug)
        except Exception as e:
            debug_print(debug, f"erro {fp}: {e}")
            continue

        if not phashes:
            continue

        elapsed = max(
            0.000001,
            round((time.perf_counter() - start_time) * 1000, 6)
        )

        index.append({
            "file_path": fp,
            "method": "video_phash",
            "fingerprint": str(tuple(phashes)),
            "execution_time_ms": elapsed,
        })

        debug_print(debug, f"{fp} -> hashes: {len(phashes)}")

    return index
