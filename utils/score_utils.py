# utils/score_utils.py

"""
score_utils.py

Gestão de scores e classificação de similaridade

- normalização de scores por método
- classificação individual (exact / near / strong)
- cálculo de score combinado
- decisão final global
"""


# CONFIG

# thresholds por método
THRESHOLDS = {
    "ssdeep": 0.7,
    "tlsh": 0.7,
    "image_phash": 0.7,
    "video_phash": 0.7,
    "audio_phash": 0.7,
    "text_simhash": 0.7,
    "fuzzy_chunks": 0.7,
}

# distâncias máximas para normalização
MAX_DISTANCE = {
    "image_phash": 64,
    "video_phash": 50,
    "tlsh": 300,
    "audio_phash": 100,
    "text_simhash": 64,
}

# pesos para score combinado
WEIGHTS = {
    "ssdeep": 0.4,
    "tlsh": 0.3,
    "image_phash": 0.3,
    "video_phash": 0.3,
    "audio_phash": 0.3,
    "text_simhash": 0.3,
    "fuzzy_chunks": 0.4,
}

# thresholds globais
STRONG_NEAR_THRESHOLD = 0.9
GLOBAL_NEAR_THRESHOLD = 0.8


# NORMALIZAÇÃO

def normalize_score(method, raw_score):
    """
    Normaliza score bruto para intervalo [0, 1].
    """

    if raw_score is None:
        return 0.0

    # métodos baseados em percentagem
    if method in ("ssdeep", "fuzzy_chunks"):
        norm = raw_score / 100.0
        return max(0.0, min(1.0, norm))

    # métodos baseados em distância
    if method in MAX_DISTANCE:

        max_dist = MAX_DISTANCE[method]

        if max_dist <= 0:
            return 0.0

        norm = 1 - (raw_score / max_dist)
        return max(0.0, min(1.0, norm))

    return 0.0


# CLASSIFICAÇÃO INDIVIDUAL

def classify_score(method, raw_score, sha_match):
    """
    Classifica score de um método individual.
    """

    norm = normalize_score(method, raw_score)

    # duplicado exato
    is_exact = (norm == 1.0) or bool(sha_match)

    threshold = THRESHOLDS.get(method, 0.8)

    # semelhante
    is_near = (
        norm >= threshold
        and norm < 1.0
    )

    # semelhante forte
    is_strong_near = (
        norm >= STRONG_NEAR_THRESHOLD
        and norm < 1.0
    )

    return norm, is_exact, is_near, is_strong_near


# SCORE COMBINADO

def compute_combined_score(scores_dict, has_exact):
    """
    Combina scores de vários métodos com pesos.
    """

    # se já houver duplicado exato
    if has_exact:
        return 1.0

    total = 0.0
    weight_sum = 0.0

    for method, score in scores_dict.items():

        if score is None:
            continue

        weight = WEIGHTS.get(method, 0.0)

        if weight <= 0:
            continue

        total += score * weight
        weight_sum += weight

    if weight_sum == 0:
        return 0.0

    result = total / weight_sum

    return max(0.0, min(1.0, result))


# CLASSIFICAÇÃO FINAL

def classify_final(combined_score, has_exact):
    """
    Classificação final global.
    """

    # tipo principal
    if has_exact:
        source_type = "exact"

    elif combined_score >= STRONG_NEAR_THRESHOLD:
        source_type = "strong_near"

    elif combined_score >= GLOBAL_NEAR_THRESHOLD:
        source_type = "near"

    else:
        source_type = "low_similarity"

    # flags auxiliares
    near_all = combined_score >= GLOBAL_NEAR_THRESHOLD

    near_exclusive = near_all and not has_exact

    strong_near_flag = (
        combined_score >= STRONG_NEAR_THRESHOLD
        and not has_exact
    )

    return source_type, near_all, near_exclusive, strong_near_flag