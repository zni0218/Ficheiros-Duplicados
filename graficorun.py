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
# 1. COMPARAÇÃO MÉTODOS (3 COLUNAS)
# ============================
plt.figure()

# dados
methods = df_all["method"]
index_time = df_all["index_time_s"]
detection_time = df_all["detection_time_s"]
total_time = df_all["total_time_s"]

# posições
x = list(range(len(methods)))

# largura das barras
width = 0.25

# barras
plt.bar([i - width for i in x], index_time, width=width, label="Indexação")
plt.bar(x, detection_time, width=width, label="Deteção")
plt.bar([i + width for i in x], total_time, width=width, label="Total")

# labels
plt.xticks(x, methods, rotation=45)
plt.ylabel("Tempo (s)")
plt.title("Comparação de Tempos por Método (run_all)")
plt.legend()

plt.tight_layout()
plt.savefig("metodos_3_colunas.png")
plt.show()



# ============================
# 2. COMPARAÇÃO GLOBAL
# ============================
labels = ["total", "validation", "index", "detection"]

all_times = [
    global_all["total_pipeline_time_s"][0],
    global_all["validation_s"][0],
    global_all["index_s"][0],
    global_all["detection_s"][0]
]


opt_times = [
    global_opt["total_pipeline_time_s"][0],
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
