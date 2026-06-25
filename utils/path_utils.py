from pathlib import Path
from utils.path_utils_safe import safe_path_obj


# CONFIG

# raiz lógica usada nos CSVs (não corresponde ao path real)
DEFAULT_DATASET_LABEL_ROOT = Path("data/inputs")


# REAL → CSV

def path_for_csv(
    file_path: Path,
    dataset_root_real: Path,
    dataset_label_root: Path = DEFAULT_DATASET_LABEL_ROOT
) -> str:
    """
    Converte path real para path armazenado no CSV.
    """

    # normalizar paths
    file_path = safe_path_obj(file_path)
    dataset_root_real = safe_path_obj(dataset_root_real)

    dataset_label_root = Path(dataset_label_root)

    try:
        # obter path relativo dentro do dataset
        relative = file_path.relative_to(dataset_root_real)

    except ValueError:
        raise ValueError(f"{file_path} não está dentro de {dataset_root_real}")

    # construir path final para CSV (sempre POSIX)
    return (dataset_label_root / relative).as_posix()


# CSV → REAL

def path_from_csv(
    csv_path: str,
    dataset_root_real: Path,
    dataset_label_root: Path = DEFAULT_DATASET_LABEL_ROOT
) -> Path:
    """
    Converte path do CSV para path real no sistema.
    """

    csv_path_obj = Path(csv_path)

    dataset_root_real = safe_path_obj(dataset_root_real)

    # label lógico (não normalizado)
    dataset_label_root = Path(dataset_label_root)

    try:
        # remover prefixo lógico
        relative = csv_path_obj.relative_to(dataset_label_root)

    except ValueError:
        # fallback (caso path já venha relativo)
        relative = csv_path_obj

    # reconstruir path real
    full_path = dataset_root_real / relative

    # normalizar antes de devolver
    return safe_path_obj(full_path)