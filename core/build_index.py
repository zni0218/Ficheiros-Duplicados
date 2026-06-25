"""
build_index.py
"""

# IMPORTS BASE

from pathlib import Path
import pandas as pd
import csv

# utilitários
from utils.path_utils import path_for_csv
from utils.file_utils import guess_mime
from utils.path_utils_safe import safe_path, safe_path_obj

# métodos
import indexing.hashing_exato as hashing_exato
import indexing.fuzzy_chunks as fuzzy_chunks
import indexing.image_phash as image_phash
import indexing.audio_phash as audio_phash
import indexing.text_simhash as text_simhash
import indexing.video_phash as video_phash
import indexing.ssdeep_hash as ssdeep_hash
import indexing.tlsh_hash as tlsh_hash


# MAPA GLOBAL DE MÉTODOS

INDEX_METHODS = {
    "hashing_exato": hashing_exato.compute_index_hashing_exato,
    "fuzzy_chunks": fuzzy_chunks.compute_index_fuzzy_chunks,
    "image_phash": image_phash.compute_index_image_phash,
    "audio_phash": audio_phash.compute_index_audio_phash,
    "text_simhash": text_simhash.compute_index_text_simhash,
    "video_phash": video_phash.compute_index_video_phash,
    "ssdeep": ssdeep_hash.compute_index_ssdeep,
    "tlsh": tlsh_hash.compute_index_tlsh,
}

ALL_METHODS = list(INDEX_METHODS.keys())



def filter_files(files, method):
    """
    Filtra ficheiros com base no método.
    """

    out = []

    for fp in files:
        try:
            mime = guess_mime(fp) or ""

            # filtros por tipo
            if method == "image_phash" and mime.startswith("image/"):
                out.append(fp)

            elif method == "audio_phash" and mime.startswith("audio/"):
                out.append(fp)

            elif method == "video_phash" and mime.startswith("video/"):
                out.append(fp)

            elif method == "text_simhash" and (
                mime.startswith("text/") or "json" in mime
            ):
                out.append(fp)

            # outros métodos aceitam tudo
            elif method not in (
                "image_phash",
                "audio_phash",
                "video_phash",
                "text_simhash",
            ):
                out.append(fp)

        except:
            continue

    return out



def merge_rows(all_rows):
    """
    Junta resultados de todos os métodos num único dataset.
    """

    combined = {}

    for method, rows in all_rows.items():
        for r in rows:

            key = r["path"]

            # cria entrada nova
            if key not in combined:
                combined[key] = {
                    "path": r["path"],
                    "abs_path": r["abs_path"]
                }

                # inicializa todos métodos
                for m in ALL_METHODS:
                    combined[key][m] = None

            # preenche fingerprint
            combined[key][method] = r["fingerprint"]

    return list(combined.values())


def write_method_csv(path: Path, rows):

    # verifica se já existe
    exists = path.exists()

    # abre em append ou write
    with open(safe_path(path), "a" if exists else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "method",
                "path",
                "fingerprint",
                "execution_time_ms",
                "abs_path"
            ]
        )

        # escreve header se for novo
        if not exists:
            writer.writeheader()

        writer.writerows(rows)


# MAIN

def build_index(base, out: Path, methods=None, debug=False):
    """
    Função principal de construção de índice.
    """

    # normaliza path
    out = safe_path_obj(out)

    # define diretoria de index
    if out.name in ("dataset_index", "session_index"):
        index_dir = out
    else:
        index_dir = out / "dataset_index"

    index_dir.mkdir(parents=True, exist_ok=True)

    # caminho do CSV combinado
    combined_path = index_dir / "combined_index.csv"

    # seleção de métodos
    if methods is None:
        selected_methods = INDEX_METHODS
    else:
        selected_methods = {
            m: INDEX_METHODS[m]
            for m in methods
            if m in INDEX_METHODS
        }

    if debug:
        print(f"[DEBUG] methods usados: {list(selected_methods.keys())}")

    # obter ficheiros
    if isinstance(base, list):
        files = base
        base_dir = Path(".")

    elif base.is_file():
        files = [base]
        base_dir = base.parent

    else:
        files = list(base.rglob("*.*"))
        base_dir = base

    # EXECUÇÃO DOS MÉTODOS

    all_rows = {}
    method_times = {}   # tempo por método

    for method, fn in selected_methods.items():

        # filtrar ficheiros válidos
        method_files = filter_files(files, method)

        if not method_files:
            continue

        try:
            raw = fn(method_files, debug=debug)
        except:
            continue

        rows = []

        # normalizar resultados
        for r in raw:
            try:
                rows.append({
                    "method": method,
                    "path": path_for_csv(r["file_path"], base_dir),
                    "fingerprint": r["fingerprint"],
                    "execution_time_ms": r.get("execution_time_ms", 0),
                    "abs_path": safe_path(r["file_path"])
                })
            except:
                continue

        if not rows:
            continue

        # calcular tempo total do método (em segundos)
        total_method_time_ms = sum(r.get("execution_time_ms", 0) for r in rows)
        total_method_time_s = total_method_time_ms / 1000

        method_times[method] = round(total_method_time_s, 4)

        # guardar CSV do método
        method_csv = index_dir / f"{method}_index.csv"
        write_method_csv(method_csv, rows)

        all_rows[method] = rows

    # nenhum método executado
    if not all_rows:
        if debug:
            print("[DEBUG] nenhum método executado")

        return {
            "method_times": method_times
        }

    # MERGE FINAL

    new_df = pd.DataFrame(merge_rows(all_rows))

    if new_df.empty:
        return {
            "method_times": method_times
        }

    # garantir todas colunas
    for m in ALL_METHODS:
        if m not in new_df.columns:
            new_df[m] = None

    # MERGE INCREMENTAL

    if combined_path.exists():
        old_df = pd.read_csv(combined_path)

        full = pd.concat([old_df, new_df], ignore_index=True)
        full = full.drop_duplicates(subset=["path"], keep="last")

    else:
        full = new_df

    # guardar CSV final
    full.to_csv(combined_path, index=False)

    if debug:
        print(f"[INDEX] total={len(full)}")

    # return com tempos por método
    return {
        "method_times": method_times
    }
