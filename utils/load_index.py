import csv
from pathlib import Path

# utilitários
from utils.path_utils import path_from_csv
from utils.path_utils_safe import safe_path


# AUTO CAST

def _auto_cast(value: str):
    """
    Converte valores do CSV para tipo correto.
    """

    if value is None or value == "":
        return None

    v = value.strip()

    # booleano
    if v.lower() in {"true", "false"}:
        return v.lower() == "true"

    # inteiro
    if v.isdigit():
        try:
            return int(v)
        except:
            pass

    # float
    try:
        return float(v)
    except:
        pass

    # fallback string
    return v


# NORMALIZE KEY

def _normalize_key(path: Path) -> str:
    """
    Normaliza path para chave consistente.
    """

    # normalização segura (unicode + resolve)
    p = Path(safe_path(path)).resolve()

    # lowercase para evitar inconsistências em Windows
    return str(p).lower()


# LOAD INDEX

def load_index(csv_path: Path, dataset_root: Path) -> dict:
    """
    Carrega CSV de index para estrutura em memória.

    """

    index = {}

    with open(safe_path(csv_path), newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:

            # converter path do CSV para path real
            real_path = path_from_csv(row["path"], dataset_root)

            # chave normalizada
            key = _normalize_key(real_path)

            index[key] = {}

            # converter campos restantes
            for k, v in row.items():

                if k == "path":
                    continue

                index[key][k] = _auto_cast(v)

    return index
