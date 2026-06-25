import pandas as pd
from pathlib import Path


# PATHS

# raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent

# cross-validation por ficheiro
CROSS_PATH = PROJECT_ROOT / "data/outputs/benchmark_cross_files.csv"

# resultados completos (run_all)
RESULTS_PATH = PROJECT_ROOT / "data/outputs/run_all/results/all_combined.csv"

# resultados completos (run_optimized)
OPTIMIZED_PATH = PROJECT_ROOT / "data/outputs/run_optimized/results/all_combined.csv"

# output final
OUT_PATH = PROJECT_ROOT / "data/outputs/benchmark_methods_final.csv"


# NORMALIZE PATHS

def normalize_path(s: str) -> str:
    """
    Normaliza paths para formato consistente.
    """
    return str(s).strip().replace("\\", "/")


# MAIN

def main():

    # carregar dados
    print("[INFO] carregar dados...")

    df_cross = pd.read_csv(CROSS_PATH)
    df_res = pd.read_csv(RESULTS_PATH)
    df_opt = pd.read_csv(OPTIMIZED_PATH)

    # marcar resultados do optimized
    df_opt["method"] = "optimizado"

    # juntar run_all + run_optimized
    df_res = pd.concat([df_res, df_opt], ignore_index=True)

    # NORMALIZAÇÃO

    df_cross["file"] = df_cross["file"].apply(normalize_path)
    df_res["file_a"] = df_res["file_a"].apply(normalize_path)
    df_res["file_b"] = df_res["file_b"].apply(normalize_path)

    results = []

    # LOOP POR MÉTODO

    for method in df_res["method"].unique():

        print(f"[INFO] método: {method}")

        df_m = df_res[df_res["method"] == method]

        pred_duplicate = {}
        pred_similar = {}

        # MAPEAR PREDIÇÕES

        for _, r in df_m.iterrows():

            f1 = r["file_a"]
            f2 = r["file_b"]

            # duplicado exato
            if r["normalized_score"] == 1.0:
                pred_duplicate[f1] = True
                pred_duplicate[f2] = True

            # semelhantes (near ou strong)
            if r["is_near_duplicate"] or r["is_strong_near_duplicate"]:
                pred_similar[f1] = True
                pred_similar[f2] = True

        # FILTRAR FICHEIROS USADOS

        files_used = set(df_m["file_a"]).union(set(df_m["file_b"]))

        dup_TP = dup_FN = 0
        sim_TP = sim_FN = 0

        # MÉTRICAS

        for _, row in df_cross.iterrows():

            f = row["file"]

            if f not in files_used:
                continue

            true_dup = bool(row["is_duplicate"])
            true_sim = bool(row["is_similar"])

            pred_dup = pred_duplicate.get(f, False)
            pred_sim = pred_similar.get(f, False)

            # DUPLICATES

            if true_dup:
                if pred_dup:
                    dup_TP += 1
                else:
                    dup_FN += 1

            # SIMILAR (ignora duplicados)

            if true_sim and not true_dup:
                if pred_sim:
                    sim_TP += 1
                else:
                    sim_FN += 1

        # cálculo recall

        dup_recall = dup_TP / (dup_TP + dup_FN) if (dup_TP + dup_FN) else 0
        sim_recall = sim_TP / (sim_TP + sim_FN) if (sim_TP + sim_FN) else 0

        # tempo total (ms)
        total_time = df_m["execution_time_ms"].sum()

        results.append({
            "method": method,
            "duplicate_success_rate": round(dup_recall *100, 4),
            "similarity_success_rate": round(sim_recall*100, 4),
            "total_execution_time_ms": round(total_time, 4),
        })

    # OUTPUT

    df_out = pd.DataFrame(results)

    df_out.to_csv(OUT_PATH, index=False)

    print("\n DONE")
    print(df_out)


# RUN

if __name__ == "__main__":
    main()
