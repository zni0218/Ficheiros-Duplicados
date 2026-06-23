import csv
from pathlib import Path

from utils.path_utils import path_from_csv
from utils.path_utils_safe import safe_path


def _auto_cast(value: str):
    """
    Converte automaticamente valores do CSV para tipo correto.
    """

    if value is None or value == "":
        return None

    v = value.strip()

    # bool
    if v.lower() in {"true", "false"}:
        return v.lower() == "true"

    # int
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

    # string (fallback)
    return v


def _normalize_key(path: Path) -> str:
    """
    Normaliza path para chave consistente (CRÍTICO).
    """

    p = Path(safe_path(path)).resolve()

    # ✅ normalização completa
    return str(p).lower()


def load_index(csv_path: Path, dataset_root: Path) -> dict:
    """
    Carrega index_global.csv com:

    ✅ Unicode safe
    ✅ tipos corretos
    ✅ paths consistentes

    Retorna:
        {
            "normalized_path": {
                "sha256": "...",
                "size": 1234,
                "score": 0.95,
                ...
            }
        }
    """

    index = {}

    with open(safe_path(csv_path), newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:

            # ✅ converter path do CSV → real
            real_path = path_from_csv(row["path"], dataset_root)

            # ✅ chave consistente
            key = _normalize_key(real_path)

            index[key] = {}

            for k, v in row.items():
                if k == "path":
                    continue

                index[key][k] = _auto_cast(v)

    return index