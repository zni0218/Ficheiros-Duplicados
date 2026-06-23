from pathlib import Path
from utils.path_utils_safe import safe_path_obj


# ============================================================
# CONFIG
# ============================================================

DEFAULT_DATASET_LABEL_ROOT = Path("data/inputs")


# ============================================================
# REAL → CSV
# ============================================================

def path_for_csv(
    file_path: Path,
    dataset_root_real: Path,
    dataset_label_root: Path = DEFAULT_DATASET_LABEL_ROOT
) -> str:

    # ✅ normalização consistente
    file_path = safe_path_obj(file_path)
    dataset_root_real = safe_path_obj(dataset_root_real)
    dataset_label_root = Path(dataset_label_root)  # ⚠️ NÃO usar safe_path aqui

    try:
        relative = file_path.relative_to(dataset_root_real)
    except ValueError:
        raise ValueError(f"{file_path} não está dentro de {dataset_root_real}")

    return (dataset_label_root / relative).as_posix()


# ============================================================
# CSV → REAL
# ============================================================

def path_from_csv(
    csv_path: str,
    dataset_root_real: Path,
    dataset_label_root: Path = DEFAULT_DATASET_LABEL_ROOT
) -> Path:

    # ✅ NÃO normalizar string aqui (evita erros de relative_to)
    csv_path_obj = Path(csv_path)

    dataset_root_real = safe_path_obj(dataset_root_real)
    dataset_label_root = Path(dataset_label_root)

    try:
        relative = csv_path_obj.relative_to(dataset_label_root)
    except ValueError:
        relative = csv_path_obj  # fallback

    full_path = dataset_root_real / relative

    return safe_path_obj(full_path)