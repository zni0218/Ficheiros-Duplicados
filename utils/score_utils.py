# ============================================================
# utils/score_utils.py
# ============================================================

# ============================================================
# CONFIGURAÇÃO GLOBAL
# ============================================================

THRESHOLDS = {
    "ssdeep": 0.85,
    "tlsh": 0.80,
    "image_phash": 0.90,
    "video_phash": 0.85,
    "audio_phash": 0.85,
    "text_simhash": 0.90,
    "fuzzy_chunks": 0.85,
}

MAX_DISTANCE = {
    "image_phash": 64,
    "video_phash": 50,
    "tlsh": 300,
    "audio_phash": 100,
    "text_simhash": 64,
}

WEIGHTS = {
    "ssdeep": 0.4,
    "tlsh": 0.3,
    "image_phash": 0.3,
    "video_phash": 0.3,
    "audio_phash": 0.3,
    "text_simhash": 0.3,
    "fuzzy_chunks": 0.4,
}

# 🔥 NÃO alterar valor → muda apenas o significado
STRONG_NEAR_THRESHOLD = 0.98

GLOBAL_NEAR_THRESHOLD = 0.85


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalize_score(method, raw_score):
    """
    Converte scores de diferentes algoritmos para [0,1].

    🔥 REGRA CRÍTICA:
    1.0 é reservado para EXACT (SHA)
    """

    if raw_score is None:
        return 0.0

    # --------------------------------------------------------
    # SIMILARIDADE DIRETA (↑ melhor)
    # --------------------------------------------------------
    if method in ("ssdeep", "fuzzy_chunks"):

        norm = raw_score / 100.0

        # 🔥 impedir que fuzzy seja exact
        if norm >= 1.0:
            return 0.999

        return max(0.0, min(1.0, norm))

    # --------------------------------------------------------
    # DISTÂNCIA (↓ melhor → inverter)
    # --------------------------------------------------------
    if method in MAX_DISTANCE:

        max_dist = MAX_DISTANCE[method]

        if max_dist <= 0:
            return 0.0

        norm = 1 - (raw_score / max_dist)

        # 🔥 impedir 1.0
        if norm >= 1.0:
            return 0.999

        return max(0.0, min(1.0, norm))

    return 0.0


# ============================================================
# CLASSIFICAÇÃO INDIVIDUAL
# ============================================================

def classify_score(method, raw_score, sha_match):
    """
    Classifica resultado de um método individual.

    Retorna:
        norm, is_exact, is_near, is_maybe_exact
    """

    norm = normalize_score(method, raw_score)

    # ✅ EXACT (único critério)
    is_exact = bool(sha_match)

    threshold = THRESHOLDS.get(method, 0.85)

    # ✅ NEAR (normal)
    is_near = (norm >= threshold) and not is_exact

    # ✅ MAYBE EXACT (novo)
    is_maybe_exact = (
        norm >= STRONG_NEAR_THRESHOLD
        and not is_exact
    )

    return norm, is_exact, is_near, is_maybe_exact


# ============================================================
# SCORE COMBINADO
# ============================================================

def compute_combined_score(scores_dict, has_exact):
    """
    Combina múltiplos métodos num score único [0,1].
    """

    # ✅ prioridade absoluta ao exact
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

    # 🔥 impedir 1.0 sem ser exact
    if result >= 1.0:
        return 0.999

    return result


# ============================================================
# CLASSIFICAÇÃO FINAL
# ============================================================

def classify_final(combined_score, has_exact):
    """
    Classificação final global.

    Retorna:
        source_type, near_all, near_exclusive, maybe_exact_flag
    """

    # --------------------------------------------------------
    # TIPO PRINCIPAL
    # --------------------------------------------------------
    if has_exact:
        source_type = "exact"

    elif combined_score >= STRONG_NEAR_THRESHOLD:
        source_type = "maybe_exact"

    elif combined_score >= GLOBAL_NEAR_THRESHOLD:
        source_type = "near"

    else:
        source_type = "low_similarity"

    # --------------------------------------------------------
    # FLAGS
    # --------------------------------------------------------
    near_all = combined_score >= GLOBAL_NEAR_THRESHOLD
    near_exclusive = near_all and not has_exact

    maybe_exact_flag = (
        combined_score >= STRONG_NEAR_THRESHOLD
        and not has_exact
    )

    return source_type, near_all, near_exclusive, maybe_exact_flag