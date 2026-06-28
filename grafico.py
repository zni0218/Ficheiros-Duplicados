import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================
# PATH (portável)
# ============================
PROJECT_ROOT = Path(__file__).resolve().parent
CSV_PATH = PROJECT_ROOT / "data" / "outputs" / "benchmark_final.csv"

# ============================
# LOAD
# ============================
df = pd.read_csv(CSV_PATH)

# remover pipelines (não têm accuracy)
df = df.dropna(subset=["duplicate_success_rate", "similarity_success_rate"])

# ============================
# EXTRAIR DADOS
# ============================
methods = df["method"]
dup_rate = df["duplicate_success_rate"]
sim_rate = df["similarity_success_rate"]

x = range(len(methods))

# ============================
# GRÁFICO
# ============================
plt.figure()

plt.bar([i - 0.2 for i in x], dup_rate, width=0.4, label="Duplicados (%)")
plt.bar([i + 0.2 for i in x], sim_rate, width=0.4, label="Semelhantes (%)")

plt.xticks(x, methods, rotation=45)
plt.ylabel("Taxa de Sucesso (%)")
plt.title("Desempenho por Método")
plt.legend()

plt.tight_layout()
plt.savefig("grafico_accuracy.png")
plt.show()