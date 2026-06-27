"""
modules/dwc/seg_moisture/calculator.py

Pure calculation functions.
No Streamlit.
No Supabase.
"""

from statistics import mean
import math


# =============================================================================
# Helpers
# =============================================================================

def _clean_numeric(values):
    """
    Removes blanks and converts valid entries to float.
    """
    cleaned = []

    for value in values:

        if value in ("", None):
            continue

        try:
            cleaned.append(float(value))
        except (TypeError, ValueError):
            continue

    return cleaned


# =============================================================================
# Segregation
# =============================================================================

def vehicle_average(samples):
    """
    Average segregation % of one vehicle.
    Blank samples are ignored.

    Returns
    -------
    float | None
    """

    samples = _clean_numeric(samples)

    if not samples:
        return None

    return round(mean(samples), 2)


def segregation_summary(vehicles):
    """
    Parameters
    ----------
    vehicles : list

    Example

    [
        {
            "vehicle": "Truck 1",
            "weight": 820,
            "samples": [81,82,80,"",79]
        },
        ...
    ]

    Returns
    -------
    {
        "overall": float,
        "vehicles_sampled": int,
        "sampled_weight": float,
        "rows": [...]
    }
    """

    rows = []

    weighted_sum = 0
    sampled_weight = 0
    vehicles_sampled = 0

    for vehicle in vehicles:

        avg = vehicle_average(vehicle.get("samples", []))

        weight = vehicle.get("weight")

        try:
            weight = float(weight)
        except Exception:
            weight = 0

        row = {
            "vehicle": vehicle.get("vehicle", ""),
            "weight": weight,
            "average": avg,
        }

        rows.append(row)

        if avg is None:
            continue

        vehicles_sampled += 1
        sampled_weight += weight
        weighted_sum += weight * avg

    overall = None
    if categories_sampled > 0:

        overall = weighted_sum
    
        if math.isnan(overall):
            overall = None
        else:
            overall = round(overall, 2)

    if sampled_weight > 0:
        overall = round(weighted_sum / sampled_weight, 2)

    return {
        "overall": overall,
        "vehicles_sampled": vehicles_sampled,
        "sampled_weight": round(sampled_weight, 2),
        "rows": rows,
    }


# =============================================================================
# Moisture
# =============================================================================

def category_average(samples):
    """
    Average moisture % for one category.
    """

    samples = _clean_numeric(samples)

    if not samples:
        return None

    return round(mean(samples), 2)


def moisture_summary(category_weights, moisture_samples):
    """
    Parameters
    ----------

    category_weights

    {
        "plastic": 520,
        "paper": 430,
        ...
    }

    moisture_samples

    {
        "plastic": [20,21,19],
        "paper": [16,17,15],
        ...
    }

    Returns
    -------

    {
        "overall": ...,
        "rows": ...
    }

    """

    total_weight = sum(category_weights.values())

    rows = []

    weighted_sum = 0

    categories_sampled = 0

    for category, weight in category_weights.items():

        avg = category_average(
            moisture_samples.get(category, [])
        )

        fraction = 0

        if total_weight > 0:
            fraction = weight / total_weight

        contribution = None

        if avg is not None:
            contribution = round(fraction * avg, 4)
            weighted_sum += fraction * avg
            categories_sampled += 1

        rows.append(
            {
                "category": category,
                "weight": round(weight, 2),
                "fraction": round(fraction, 4),
                "average": avg,
                "contribution": contribution,
            }
        )

    overall = None

    if categories_sampled:
        overall = round(weighted_sum, 2)

    return {
        "overall": overall,
        "categories_sampled": categories_sampled,
        "total_weight": round(total_weight, 2),
        "rows": rows,
    }
