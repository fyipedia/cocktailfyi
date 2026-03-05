"""Cocktail computation engine — stateless pure functions.

All functions operate on primitive types (str, dict, list, Decimal)
with zero external dependencies. Extracted from the CocktailFYI Django app.
"""

from __future__ import annotations

import contextlib
import re
from decimal import Decimal
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Conversion factors to milliliters
UNIT_TO_ML: dict[str, float] = {
    "oz": 30.0,
    "cl": 10.0,
    "ml": 1.0,
    "tsp": 5.0,
    "tbsp": 15.0,
    "shot": 45.0,
    "cup": 240.0,
    "part": 30.0,
    "parts": 30.0,
    "dash": 1.0,
    "dashes": 1.0,
    "drop": 0.5,
    "drops": 0.5,
    "splash": 5.0,
    "jigger": 45.0,
    "pint": 473.0,
    "glass": 240.0,
    "can": 355.0,
    "bottle": 750.0,
    "fifth": 750.0,
}

# Descriptive measures that carry negligible volume
DESCRIPTIVE_MEASURES: set[str] = {
    "to taste",
    "splash",
    "dash",
    "drop",
    "garnish",
    "top",
    "top up",
    "fill",
    "float",
    "pinch",
    "twist",
    "wedge",
    "slice",
    "sprig",
    "leaf",
    "leaves",
}

# Techniques considered "hard" for difficulty scoring
HARD_TECHNIQUES: set[str] = {
    "muddling",
    "layering",
    "smoking",
    "flaming",
    "sous vide",
    "fat-washing",
    "infusing",
}

# Alcohol dilution factor (~22% dilution from shaking/stirring with ice)
DILUTION_FACTOR: float = 0.78


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_fraction(s: str) -> float:
    """Parse '1 1/2' or '3/4' into float.

    Handles:
      - '3/4'      -> 0.75
      - '1 1/2'    -> 1.5
      - '2'        -> 2.0
      - '1.5'      -> 1.5
      - ''         -> 0.0
    """
    s = s.strip()
    if not s:
        return 0.0

    # Try plain float first
    try:
        return float(s)
    except ValueError:
        pass

    # Mixed fraction: "1 1/2"
    parts = s.split()
    total = 0.0
    for part in parts:
        if "/" in part:
            with contextlib.suppress(ValueError, ZeroDivisionError):
                num_str, den_str = part.split("/", 1)
                total += float(num_str) / float(den_str)
        else:
            with contextlib.suppress(ValueError):
                total += float(part)
    return total


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_measure_ml(measure: str) -> float:
    """Parse a cocktail measure string into milliliters.

    Examples::

        >>> parse_measure_ml("1 1/2 oz")
        45.0
        >>> parse_measure_ml("2 cl")
        20.0
        >>> parse_measure_ml("30 ml")
        30.0
        >>> parse_measure_ml("1 tsp")
        5.0
        >>> parse_measure_ml("splash")
        5.0
        >>> parse_measure_ml("")
        30.0
    """
    if not measure or not measure.strip():
        return 30.0

    cleaned = measure.strip().lower()

    # Check descriptive measures
    for desc in DESCRIPTIVE_MEASURES:
        if desc in cleaned:
            return 5.0

    # Try to extract a numeric + unit pattern
    # Matches: "1 1/2 oz", "30 ml", "3/4 cl", "2 parts", etc.
    pattern = r"^([\d\s/\.]+)\s*([a-z]+)?"
    match = re.match(pattern, cleaned)

    if match:
        number_str = match.group(1).strip()
        unit_str = (match.group(2) or "").strip()

        amount = _parse_fraction(number_str)
        if amount <= 0:
            amount = 1.0

        # Look up unit conversion
        ml_per_unit = UNIT_TO_ML.get(unit_str, 0.0)
        if ml_per_unit > 0:
            return amount * ml_per_unit

        # No unit recognized -- assume oz
        if unit_str == "" and amount > 0:
            return amount * 30.0

    # Fallback: unparseable measure
    return 30.0


def estimate_abv(ingredients: list[dict[str, Any]]) -> Decimal:
    """Estimate cocktail ABV from ingredient list.

    Each dict should have:
        - ``measure`` (str): measure string like ``"1 1/2 oz"``
        - ``abv`` (float | None): alcohol by volume percentage (e.g. 40.0)

    Applies ~22% dilution factor from ice/shaking.

    Returns:
        ABV as a percentage (e.g. ``Decimal('18.50')``).

    Example::

        >>> estimate_abv([
        ...     {"measure": "2 oz", "abv": 40.0},
        ...     {"measure": "1 oz", "abv": 0},
        ...     {"measure": "1 oz", "abv": 0},
        ... ])
        Decimal('7.80')
    """
    total_ml = 0.0
    total_alcohol_ml = 0.0

    for ing in ingredients:
        measure = ing.get("measure", "")
        abv_pct = ing.get("abv")

        vol_ml = parse_measure_ml(str(measure) if measure else "")
        total_ml += vol_ml

        if abv_pct is not None and abv_pct > 0:
            total_alcohol_ml += vol_ml * (float(abv_pct) / 100.0)

    if total_ml <= 0:
        return Decimal("0.00")

    raw_abv = (total_alcohol_ml / total_ml) * 100.0
    diluted_abv = raw_abv * DILUTION_FACTOR

    return Decimal(str(round(diluted_abv, 2)))


def estimate_calories(ingredients: list[dict[str, Any]]) -> int:
    """Estimate total calories for a cocktail.

    Each dict should have:
        - ``measure`` (str): measure string
        - ``calories_per_100ml`` (float | None): calorie density
        - ``abv`` (float | None): alcohol by volume percentage

    For ingredients without calorie data but with ABV:
        ``alcohol calories = volume_ml * (abv/100) * 0.789 g/ml * 7 cal/g``

    Returns:
        Estimated total calories (rounded to nearest integer).

    Example::

        >>> estimate_calories([
        ...     {"measure": "2 oz", "abv": 40.0, "calories_per_100ml": None},
        ...     {"measure": "1 oz", "abv": 0, "calories_per_100ml": 40},
        ... ])
        145
    """
    total_calories = 0.0

    for ing in ingredients:
        measure = ing.get("measure", "")
        cal_per_100 = ing.get("calories_per_100ml")
        abv_pct = ing.get("abv")

        vol_ml = parse_measure_ml(str(measure) if measure else "")

        if cal_per_100 is not None and cal_per_100 > 0:
            total_calories += vol_ml * (float(cal_per_100) / 100.0)
        elif abv_pct is not None and abv_pct > 0:
            # Alcohol: 0.789 g/ml density, 7 kcal/g
            alcohol_ml = vol_ml * (float(abv_pct) / 100.0)
            alcohol_grams = alcohol_ml * 0.789
            total_calories += alcohol_grams * 7.0

    return round(total_calories)


def compute_flavor_profile(ingredients: list[dict[str, Any]]) -> dict[str, int]:
    """Compute weighted-average flavor profile (0-10 scale).

    Each dict should have:
        - ``measure`` (str): measure string
        - ``flavor_sweet`` (int): 0-10
        - ``flavor_sour`` (int): 0-10
        - ``flavor_bitter`` (int): 0-10
        - ``flavor_strong`` (int): 0-10

    Weight is volume in ml.

    Returns:
        Dict with keys ``sweet``, ``sour``, ``bitter``, ``strong`` (int 0-10).

    Example::

        >>> compute_flavor_profile([
        ...     {"measure": "2 oz", "flavor_sweet": 2,
        ...      "flavor_sour": 0, "flavor_bitter": 0, "flavor_strong": 8},
        ...     {"measure": "1 oz", "flavor_sweet": 8,
        ...      "flavor_sour": 7, "flavor_bitter": 0, "flavor_strong": 0},
        ... ])
        {'sweet': 4, 'sour': 2, 'bitter': 0, 'strong': 5}
    """
    total_weight = 0.0
    weighted_sweet = 0.0
    weighted_sour = 0.0
    weighted_bitter = 0.0
    weighted_strong = 0.0

    for ing in ingredients:
        measure = ing.get("measure", "")
        vol_ml = parse_measure_ml(str(measure) if measure else "")

        sweet = ing.get("flavor_sweet", 0) or 0
        sour = ing.get("flavor_sour", 0) or 0
        bitter = ing.get("flavor_bitter", 0) or 0
        strong = ing.get("flavor_strong", 0) or 0

        total_weight += vol_ml
        weighted_sweet += vol_ml * sweet
        weighted_sour += vol_ml * sour
        weighted_bitter += vol_ml * bitter
        weighted_strong += vol_ml * strong

    if total_weight <= 0:
        return {"sweet": 0, "sour": 0, "bitter": 0, "strong": 0}

    return {
        "sweet": min(10, max(0, round(weighted_sweet / total_weight))),
        "sour": min(10, max(0, round(weighted_sour / total_weight))),
        "bitter": min(10, max(0, round(weighted_bitter / total_weight))),
        "strong": min(10, max(0, round(weighted_strong / total_weight))),
    }


def compute_difficulty(ingredient_count: int, techniques: list[str] | None = None) -> str:
    """Compute difficulty level for a cocktail.

    Args:
        ingredient_count: Number of ingredients.
        techniques: List of technique names (e.g. ``["muddling", "shaking"]``).

    Returns:
        ``"easy"``, ``"medium"``, or ``"hard"``.

    Rules:
        - **Hard**: >= 6 ingredients OR any hard technique
        - **Medium**: >= 4 ingredients OR >= 2 techniques
        - **Easy**: otherwise

    Example::

        >>> compute_difficulty(3, ["shaking"])
        'easy'
        >>> compute_difficulty(5, ["muddling"])
        'hard'
        >>> compute_difficulty(4)
        'medium'
    """
    techs = techniques or []
    techs_lower = [t.lower() for t in techs]

    # Check for hard techniques
    has_hard_technique = any(t in HARD_TECHNIQUES for t in techs_lower)
    if has_hard_technique or ingredient_count >= 6:
        return "hard"

    if ingredient_count >= 4 or len(techs) >= 2:
        return "medium"

    return "easy"
