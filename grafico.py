import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
# PATH
CSV_PATH = PROJECT_ROOT / "data" / "outputs" / "benchmark_final.csv"

df = pd.read_csv(CSV_PATH)

# extrair dados
methods = df["method"]
times = df["total_time_s"]

# gráfico
plt.figure()
plt.bar(methods, times)

plt.title("Tempo total por método")
plt.xlabel("Método")
plt.ylabel("Tempo (s)")

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("grafico_metodos.png")
plt.show()