from database import get_connection


# =========================================================
# TOOL 1: SEARCH TRIALS
# =========================================================

def search_trials(
    crop=None,
    product=None,
    country=None,
    year=None,
    trial_type=None,
):
    """
    Search normalized trial records using structured filters.
    """

    conn = get_connection()

    query = """
        SELECT
            trial_id,
            crop,
            product,
            country,
            year,
            trial_type,
            treatment_yield_kg_ha,
            control_yield_kg_ha,
            source,
            notes
        FROM trials
        WHERE 1=1
    """

    params = []

    if crop:
        query += " AND LOWER(crop) = LOWER(?)"
        params.append(crop)

    if product:
        query += " AND LOWER(product) = LOWER(?)"
        params.append(product)

    if country:
        query += " AND LOWER(country) = LOWER(?)"
        params.append(country)

    if year:
        query += " AND year = ?"
        params.append(year)

    if trial_type:
        query += " AND LOWER(trial_type) = LOWER(?)"
        params.append(trial_type)

    query += " ORDER BY year, trial_id"

    cursor = conn.execute(query, params)

    rows = cursor.fetchall()

    conn.close()

    results = []

    for row in rows:

        results.append({
            "trial_id": row[0],
            "crop": row[1],
            "product": row[2],
            "country": row[3],
            "year": row[4],
            "trial_type": row[5],
            "treatment_yield_kg_ha": row[6],
            "control_yield_kg_ha": row[7],
            "source": row[8],
            "notes": row[9],
        })

    return results


# =========================================================
# TOOL 2: COMPARE TRIALS
# =========================================================

def compare_trials(trial_ids):
    """
    Compare treatment and control results for selected trials.
    """

    conn = get_connection()

    placeholders = ",".join(
        ["?"] * len(trial_ids)
    )

    query = f"""
        SELECT
            trial_id,
            crop,
            product,
            country,
            year,
            trial_type,
            treatment_yield_kg_ha,
            control_yield_kg_ha,
            source
        FROM trials
        WHERE trial_id IN ({placeholders})
        ORDER BY year, trial_id
    """

    cursor = conn.execute(
        query,
        trial_ids
    )

    rows = cursor.fetchall()

    conn.close()

    results = []

    for row in rows:

        treatment = row[6]
        control = row[7]

        absolute_change = None
        percentage_change = None

        if treatment is not None and control is not None:

            absolute_change = (
                treatment - control
            )

            if control != 0:

                percentage_change = (
                    absolute_change / control
                ) * 100

        results.append({
            "trial_id": row[0],
            "crop": row[1],
            "product": row[2],
            "country": row[3],
            "year": row[4],
            "trial_type": row[5],
            "treatment_yield_kg_ha": treatment,
            "control_yield_kg_ha": control,
            "absolute_change_kg_ha": absolute_change,
            "percentage_change": percentage_change,
            "source": row[8],
        })

    return results


# =========================================================
# TOOL 3: FIND EVIDENCE
# =========================================================

def find_evidence(
    crop=None,
    product=None,
):
    """
    Find trial evidence for a crop/product combination.
    """

    trials = search_trials(
        crop=crop,
        product=product,
    )

    evidence = []

    for trial in trials:

        treatment = trial[
            "treatment_yield_kg_ha"
        ]

        control = trial[
            "control_yield_kg_ha"
        ]

        effect = None

        if treatment is not None and control is not None:

            effect = treatment - control

        evidence.append({
            "trial_id": trial["trial_id"],
            "crop": trial["crop"],
            "product": trial["product"],
            "country": trial["country"],
            "year": trial["year"],
            "trial_type": trial["trial_type"],
            "treatment_yield_kg_ha": treatment,
            "control_yield_kg_ha": control,
            "yield_difference_kg_ha": effect,
            "source": trial["source"],
            "notes": trial["notes"],
        })

    return evidence


# =========================================================
# TOOL 4: GET ORIGINAL SOURCES
# =========================================================

def get_trial_sources(trial_id):
    """
    Return all original sources associated with a trial.
    """

    conn = get_connection()

    cursor = conn.execute("""
        SELECT
            trial_id,
            source,
            source_type,
            treatment_yield_kg_ha,
            control_yield_kg_ha,
            notes
        FROM trial_sources
        WHERE trial_id = ?
        ORDER BY source
    """, (trial_id,))

    rows = cursor.fetchall()

    conn.close()

    sources = []

    for row in rows:

        sources.append({
            "trial_id": row[0],
            "source": row[1],
            "source_type": row[2],
            "treatment_yield_kg_ha": row[3],
            "control_yield_kg_ha": row[4],
            "notes": row[5],
        })

    return sources