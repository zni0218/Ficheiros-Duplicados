"""
fuzzy_chunks.py

Geração de fingerprints baseada em blocos

- divide ficheiro em chunks
- aplica sampling (início / meio / fim)
- reduz tamanho do fingerprint
"""

from pathlib import Path
import time

from utils.file_utils import chunk_hashes


# DEBUG

def debug_print(debug: bool, msg: str):
    if debug:
        print(f"[DEBUG] {msg}")


# CONFIG

# número máximo de chunks usados
MAX_CHUNKS = 12


# SAMPLING

def sample_chunks(chunks: list[str], max_chunks=MAX_CHUNKS):
    """
    Seleciona subconjunto de chunks:
    início, meio e fim.
    """

    n = len(chunks)

    if n <= max_chunks:
        return chunks

    # distribuição uniforme
    n_start = max_chunks // 3
    n_end = max_chunks // 3
    n_mid = max_chunks - n_start - n_end

    # início
    start = chunks[:n_start]

    # meio
    mid_start = max(0, (n // 2) - (n_mid // 2))
    mid = chunks[mid_start: mid_start + n_mid]

    # fim
    end = chunks[-n_end:]

    return start + mid + end


# INDEXAÇÃO

def compute_index_fuzzy_chunks(files: list[Path], debug=False):
    """
    Gera fingerprints fuzzy_chunks para ficheiros.
    """

    debug_print(debug, "Index fuzzy_chunks")

    index = []

    for fp in files:

        start_time = time.perf_counter()

        try:
            # gerar hashes por blocos
            chunks = chunk_hashes(fp)

            # reduzir número de chunks
            chunks = sample_chunks(chunks)

        except Exception:
            continue

        # tempo por ficheiro (ms)
        elapsed = max(
            0.000001,
            round((time.perf_counter() - start_time) * 1000, 6)
        )

        # converter para formato compacto (evita CSV gigante)
        fp_repr = str(tuple(chunks))

        index.append({
            "file_path": fp,
            "method": "fuzzy_chunks",
            "fingerprint": fp_repr,
            "execution_time_ms": elapsed,
        })

        # debug opcional
        if debug:
            debug_print(debug, f"{fp} -> chunks usados: {len(chunks)}")

    return index
