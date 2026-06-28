import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================
# PATH BASE (portável)
# ============================
PROJECT_ROOT = Path(__file__).resolve().parent

# run_all
RUN_ALL_METHODS = PROJECT_ROOT / "data" / "outputs" / "run_all" / "performance" / "performance_methods.csv"
RUN_ALL_GLOBAL = PROJECT_ROOT / "data" / "outputs" / "run_all" / "performance" / "performance_global.csv"


# optimized
RUN_OPT_METHODS = PROJECT_ROOT / "data" / "outputs" / "run_optimized" / "performance" / "performance_methods.csv"
RUN_OPT_GLOBAL = PROJECT_ROOT / "data" / "outputs" / "run_optimized" / "performance" / "performance_global.csv"

# ============================
# LOAD
# ============================
df_all = pd.read_csv(RUN_ALL_METHODS)


global_all = pd.read_csv(RUN_ALL_GLOBAL)
global_opt = pd.read_csv(RUN_OPT_GLOBAL)


# ============================
# 1. COMPARAÇÃO MÉTODOS
# ============================
plt.figure()

# garantir que só compara métodos comuns
common_methods = set(df_all["method"])

df_all_filtered = df_all[df_all["method"].isin(common_methods)]


# ordenar igual
df_all_filtered = df_all_filtered.set_index("method").loc[sorted(common_methods)]

x = range(len(common_methods))

plt.bar([i - 0.2 for i in x], df_all_filtered["total_time_s"], width=0.4, label="run_all")


plt.xticks(x, df_all_filtered.index, rotation=45)
plt.ylabel("Tempo total (s)")
plt.title("Comparação de Métodos: run_all")
plt.legend()
plt.tight_layout()

plt.savefig("comparacao_metodos.png")
plt.show()


# ============================
# 2. COMPARAÇÃO GLOBAL
# ============================
labels = ["validation", "index", "detection"]

all_times = [
    global_all["validation_s"][0],
    global_all["index_s"][0],
    global_all["detection_s"][0]
]


opt_times = [
    global_opt["validation_s"][0],
    global_opt["index_s"][0],
    global_opt["detection_s"][0]
]

x = range(len(labels))

plt.figure()

plt.bar([i - 0.2 for i in x], all_times, width=0.4, label="run_all")
plt.bar([i + 0.2 for i in x], opt_times, width=0.4, label="optimized")

plt.xticks(x, labels)
plt.ylabel("Tempo (s)")
plt.title("Comparação Global do Pipeline")
plt.legend()
plt.tight_layout()

plt.savefig("comparacao_global.png")
plt.show()


# ============================
# 3. PRINT RESUMO (ÚTIL PARA RELATÓRIO)
# ============================
print("=== TOTAL PIPELINE ===")
print(f"run_all      : {global_all['total_pipeline_time_s'][0]:.2f}s")
print(f"optimized    : {global_opt['total_pipeline_time_s'][0]:.2f}s")

speedup = global_all['total_pipeline_time_s'][0] / global_opt['total_pipeline_time_s'][0]
print(f"Speedup      : {speedup:.2f}x")
