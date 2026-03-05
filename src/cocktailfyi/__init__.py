"""cocktailfyi — Cocktail computation engine for developers.

Parse cocktail measures, estimate ABV and calories, compute flavor profiles,
and score recipe difficulty. Zero dependencies. <1ms per computation.

Usage::

    from cocktailfyi import parse_measure_ml, estimate_abv, estimate_calories

    ml = parse_measure_ml("1 1/2 oz")  # 45.0

    abv = estimate_abv([
        {"measure": "2 oz", "abv": 40.0},
        {"measure": "1 oz", "abv": 0},
    ])
    print(abv)  # Decimal('20.80')
"""

from cocktailfyi.engine import (
    DESCRIPTIVE_MEASURES,
    DILUTION_FACTOR,
    HARD_TECHNIQUES,
    UNIT_TO_ML,
    compute_difficulty,
    compute_flavor_profile,
    estimate_abv,
    estimate_calories,
    parse_measure_ml,
)

__version__ = "0.1.0"

__all__ = [
    "DESCRIPTIVE_MEASURES",
    "DILUTION_FACTOR",
    "HARD_TECHNIQUES",
    "UNIT_TO_ML",
    "compute_difficulty",
    "compute_flavor_profile",
    "estimate_abv",
    "estimate_calories",
    "parse_measure_ml",
]
