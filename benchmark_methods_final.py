"""
benchmark_final.py

Objetivo:
Comparar desempenho de:

- métodos individuais (run_all)
- pipeline otimizado (run_optimized)

Métricas avaliadas:
- taxa de deteção de duplicados
- taxa de deteção de semelhantes
- tempo real de execução
"""

import pandas as pd
from pathlib import Path


# PATHS


# raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent

# cross-validation por ficheiro (ground truth)
CROSS_PATH = PROJECT_ROOT / "data/outputs/benchmark_cross_files.csv"

# resultados do run_all
RESULTS_PATH = PROJECT_ROOT / "data/outputs/run_all/results/all_combined.csv"
PERF_METHODS_PATH = PROJECT_ROOT / "data/outputs/run_all/performance/performance_methods.csv"
PERF_GLOBAL_PATH = PROJECT_ROOT / "data/outputs/run_all/performance/performance_global.csv"

# resultados do run_optimized
OPTIMIZED_PATH = PROJECT_ROOT / "data/outputs/run_optimized/results/all_combined.csv"
PERF_OPT_PATH = PROJECT_ROOT / "data/outputs/run_optimized/performance/performance_global.csv"

# output final
OUT_FINAL = PROJECT_ROOT / "data/outputs/benchmark_final.csv"



# NORMALIZE PATHS


def normalize_path(s):
    """
    Normaliza paths para formato consistente.
    (evita problemas Windows vs Linux)
    """
    return str(s).strip().replace("\\", "/")



# METRICS (RECALL POR FICHEIRO)


def compute_metrics(df_cross, df_res):
    """
    Calcula taxa de sucesso por ficheiro:

    - duplicados exatos
    - semelhantes (near + strong)

    Baseado em cross-validation.
    """

    pred_dup = {}
    pred_sim = {}

    # -----------------------------
    # MAPEAR PREVISÕES
    # -----------------------------

    for _, r in df_res.iterrows():
        f1, f2 = r["file_a"], r["file_b"]

        # duplicado exato
        if r["normalized_score"] == 1.0:
            pred_dup[f1] = True
            pred_dup[f2] = True

        # semelhante
        if r["is_near_duplicate"] or r["is_strong_near_duplicate"]:
            pred_sim[f1] = True
            pred_sim[f2] = True

    # ficheiros usados pelo método
    files_used = set(df_res["file_a"]).union(set(df_res["file_b"]))

    # métricas
    dup_TP = dup_FN = 0
    sim_TP = sim_FN = 0

    # -----------------------------
    # COMPARAÇÃO COM GROUND TRUTH
    # -----------------------------

    for _, row in df_cross.iterrows():

        f = row["file"]

        if f not in files_used:
            continue

        true_dup = bool(row["is_duplicate"])
        true_sim = bool(row["is_similar"])

        pred_d = pred_dup.get(f, False)
        pred_s = pred_sim.get(f, False)

        # DUPLICADOS
        if true_dup:
            if pred_d:
                dup_TP += 1
            else:
                dup_FN += 1

        # SIMILARES (ignora duplicados)
        if true_sim and not true_dup:
            if pred_s:
                sim_TP += 1
            else:
                sim_FN += 1

    # recall
    dup_recall = dup_TP / (dup_TP + dup_FN) if (dup_TP + dup_FN) else 0
    sim_recall = sim_TP / (sim_TP + sim_FN) if (sim_TP + sim_FN) else 0

    return round(dup_recall * 100, 4), round(sim_recall * 100, 4)



# MAIN


def main():

    print("[INFO] loading data...")

    # carregar dados
    df_cross = pd.read_csv(CROSS_PATH)

    df_res = pd.read_csv(RESULTS_PATH)
    df_perf = pd.read_csv(PERF_METHODS_PATH)
    df_perf_global = pd.read_csv(PERF_GLOBAL_PATH)
    df_opt = pd.read_csv(OPTIMIZED_PATH)
    df_perf_opt = pd.read_csv(PERF_OPT_PATH)

    # -----------------------------
    # NORMALIZAÇÃO PATHS
    # -----------------------------

    df_cross["file"] = df_cross["file"].apply(normalize_path)
    df_res["file_a"] = df_res["file_a"].apply(normalize_path)
    df_res["file_b"] = df_res["file_b"].apply(normalize_path)
    df_opt["file_a"] = df_opt["file_a"].apply(normalize_path)
    df_opt["file_b"] = df_opt["file_b"].apply(normalize_path)

    final_results = []

    # ==================================================
    # MÉTODOS INDIVIDUAIS (run_all)
    # ==================================================

    for method in df_res["method"].unique():

        print(f"[INFO] method: {method}")

        df_m = df_res[df_res["method"] == method]

        # cálculo métricas
        dup_rate, sim_rate = compute_metrics(df_cross, df_m)

        # tempo real do performance_methods.csv
        perf_row = df_perf[df_perf["method"] == method]
        total_time = perf_row.iloc[0]["total_time_s"] if not perf_row.empty else 0

        final_results.append({
            "method": method,
            "duplicate_success_rate": dup_rate,
            "similarity_success_rate": sim_rate,
            "total_time_s": round(total_time, 4)
        })

    # ==================================================
    # TOTAL RUN_ALL
    # ==================================================

    print("[INFO] calcular total run_all...")

    run_all_total_time = df_perf_global.iloc[0]["total_pipeline_time_s"]

    final_results.append({
        "method": "pipeline_run_all",
        "duplicate_success_rate": None,  # não aplicável
        "similarity_success_rate": None,  # não aplicável
        "total_time_s": round(run_all_total_time, 4)
    })
    # PIPELINE OTIMIZADO


    print("[INFO] pipeline optimized...")

    dup_rate, sim_rate = compute_metrics(df_cross, df_opt)

    # tempo real do pipeline
    real_time = df_perf_opt.iloc[0]["total_pipeline_time_s"]

    final_results.append({
        "method": "pipeline_optimized",
        "duplicate_success_rate": dup_rate,
        "similarity_success_rate": sim_rate,
        "total_time_s": round(real_time, 4)
    })

    # SAVE FINAL


    df_final = pd.DataFrame(final_results)
    df_final.to_csv(OUT_FINAL, index=False)

    print("\n DONE")
    print(df_final)



# RUN

if __name__ == "__main__":
    main()