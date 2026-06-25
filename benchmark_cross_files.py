"""
benchmark_cross_files.py

Agrega resultados por ficheiro a partir do ALL_combined.csv

- converte A vs B → estado por ficheiro
- identifica duplicados e semelhantes
- usado para avaliação global
"""

import pandas as pd
from pathlib import Path


# INPUT / OUTPUT

# raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent

# CSV vindo do run_all (comparações par-a-par)
INPUT_CSV = PROJECT_ROOT / "data/outputs/run_all/results/all_combined.csv"

# CSV agregado por ficheiro
OUTPUT_CSV = PROJECT_ROOT / "data/outputs/benchmark_cross_files.csv"


# BUILD CROSS VALIDATION POR FILE

def build_cross_validation_by_file(df):
    """
    Converte resultados par-a-par (file_a, file_b)
    para estado individual por ficheiro:
        file | is_duplicate | is_similar
    """

    file_map = {}

    for _, r in df.iterrows():

        a = r["file_a"]
        b = r["file_b"]

        # processa ambos os ficheiros
        for file in (a, b):

            entry = file_map.setdefault(file, {
                "file": file,
                "is_duplicate": False,
                "is_similar": False
            })

            # duplicado exato
            if r["normalized_score"] == 1.0:
                entry["is_duplicate"] = True

            # semelhante (near ou strong)
            if r["is_near_duplicate"] or r["is_strong_near_duplicate"]:
                entry["is_similar"] = True

    return pd.DataFrame(file_map.values())


# MAIN

def main():

    # carregar CSV base
    print("[INFO] a ler CSV...")
    df = pd.read_csv(INPUT_CSV)

    # construir agregação por ficheiro
    print("[INFO] a construir cross-validation por ficheiro...")
    cross_df = build_cross_validation_by_file(df)

    # guardar resultado
    print("[INFO] a guardar...")

    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    cross_df.to_csv(OUTPUT_CSV, index=False)

    print("\n DONE")
    print(f"Output: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
