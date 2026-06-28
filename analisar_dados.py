import pandas as pd
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
# PATH
CSV_PATH = PROJECT_ROOT / "data" / "outputs" / "benchmark_cross_files.csv"

# carregar dados
df = pd.read_csv(CSV_PATH)

# garantir booleanos
df["is_duplicate"] = df["is_duplicate"].astype(bool)
df["is_similar"] = df["is_similar"].astype(bool)

# contagens
total = len(df)

duplicates = df["is_duplicate"].sum()
similar = df["is_similar"].sum()

# ambos falsos
both_false = ((~df["is_duplicate"]) & (~df["is_similar"])).sum()

# output
print("TOTAL:", total)
print("DUPLICATES (True):", duplicates)
print("SIMILAR (True):", similar)
print("BOTH FALSE:", both_false)

# extra (opcional, útil)
both_true = ((df["is_duplicate"]) & (df["is_similar"])).sum()
print("BOTH TRUE:", both_true)
