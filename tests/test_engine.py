"""Tests for cocktailfyi.engine — measure parsing, ABV, calories, flavor, difficulty."""

from decimal import Decimal

import pytest

from cocktailfyi import (
    compute_difficulty,
    compute_flavor_profile,
    estimate_abv,
    estimate_calories,
    parse_measure_ml,
)

# ---------------------------------------------------------------------------
# parse_measure_ml
# ---------------------------------------------------------------------------


class TestParseMeasureMl:
    def test_empty_string(self) -> None:
        assert parse_measure_ml("") == 30.0

    def test_whitespace(self) -> None:
        assert parse_measure_ml("   ") == 30.0

    def test_oz(self) -> None:
        assert parse_measure_ml("1 oz") == 30.0

    def test_oz_fraction(self) -> None:
        assert parse_measure_ml("1 1/2 oz") == 45.0

    def test_cl(self) -> None:
        assert parse_measure_ml("2 cl") == 20.0

    def test_ml(self) -> None:
        assert parse_measure_ml("30 ml") == 30.0

    def test_tsp(self) -> None:
        assert parse_measure_ml("1 tsp") == 5.0

    def test_tbsp(self) -> None:
        assert parse_measure_ml("2 tbsp") == 30.0

    def test_shot(self) -> None:
        assert parse_measure_ml("1 shot") == 45.0

    def test_cup(self) -> None:
        assert parse_measure_ml("1 cup") == 240.0

    def test_parts(self) -> None:
        assert parse_measure_ml("3 parts") == 90.0

    def test_splash(self) -> None:
        assert parse_measure_ml("splash") == 5.0

    def test_to_taste(self) -> None:
        assert parse_measure_ml("to taste") == 5.0

    def test_garnish(self) -> None:
        assert parse_measure_ml("garnish") == 5.0

    def test_dash(self) -> None:
        # "dashes" contains "dash" (descriptive measure) → 5.0
        assert parse_measure_ml("2 dashes") == 5.0

    def test_drop(self) -> None:
        # "drop" is in DESCRIPTIVE_MEASURES, so returns 5.0
        assert parse_measure_ml("drop") == 5.0

    def test_number_only(self) -> None:
        # No unit → assume oz (30ml)
        assert parse_measure_ml("2") == 60.0

    def test_fraction_only(self) -> None:
        assert parse_measure_ml("3/4 oz") == 22.5

    def test_jigger(self) -> None:
        assert parse_measure_ml("1 jigger") == 45.0

    def test_pint(self) -> None:
        assert parse_measure_ml("1 pint") == 473.0

    def test_bottle(self) -> None:
        assert parse_measure_ml("1 bottle") == 750.0


# ---------------------------------------------------------------------------
# estimate_abv
# ---------------------------------------------------------------------------


class TestEstimateAbv:
    def test_single_spirit(self) -> None:
        result = estimate_abv([{"measure": "2 oz", "abv": 40.0}])
        assert result == Decimal("31.20")

    def test_with_mixer(self) -> None:
        result = estimate_abv(
            [
                {"measure": "2 oz", "abv": 40.0},
                {"measure": "4 oz", "abv": 0},
            ]
        )
        # raw = (60*0.4)/(180) * 100 = 13.33, diluted = 13.33 * 0.78 = 10.40
        assert result == Decimal("10.40")

    def test_no_alcohol(self) -> None:
        result = estimate_abv(
            [
                {"measure": "4 oz", "abv": 0},
                {"measure": "2 oz", "abv": None},
            ]
        )
        assert result == Decimal("0.00")

    def test_empty_list(self) -> None:
        result = estimate_abv([])
        assert result == Decimal("0.00")

    def test_missing_measure(self) -> None:
        # Missing measure defaults to 30ml
        result = estimate_abv([{"abv": 40.0}])
        assert result == Decimal("31.20")


# ---------------------------------------------------------------------------
# estimate_calories
# ---------------------------------------------------------------------------


class TestEstimateCalories:
    def test_with_calories_per_100ml(self) -> None:
        result = estimate_calories([{"measure": "100 ml", "calories_per_100ml": 200, "abv": 0}])
        assert result == 200

    def test_with_abv_only(self) -> None:
        # 60ml * 0.40 * 0.789 * 7 = 132.55
        result = estimate_calories([{"measure": "2 oz", "abv": 40.0, "calories_per_100ml": None}])
        assert result == 133

    def test_mixed(self) -> None:
        result = estimate_calories(
            [
                {"measure": "2 oz", "abv": 40.0, "calories_per_100ml": None},
                {"measure": "1 oz", "abv": 0, "calories_per_100ml": 40},
            ]
        )
        # Spirit: 60 * 0.4 * 0.789 * 7 = 132.55
        # Mixer: 30 * 0.4 = 12.0
        assert result == 145

    def test_empty_list(self) -> None:
        assert estimate_calories([]) == 0

    def test_no_data(self) -> None:
        # No abv or calories → 0
        result = estimate_calories([{"measure": "1 oz", "abv": None, "calories_per_100ml": None}])
        assert result == 0


# ---------------------------------------------------------------------------
# compute_flavor_profile
# ---------------------------------------------------------------------------


class TestComputeFlavorProfile:
    def test_basic_profile(self) -> None:
        profile = compute_flavor_profile(
            [
                {
                    "measure": "2 oz",
                    "flavor_sweet": 0,
                    "flavor_sour": 0,
                    "flavor_bitter": 0,
                    "flavor_strong": 10,
                },
                {
                    "measure": "1 oz",
                    "flavor_sweet": 10,
                    "flavor_sour": 8,
                    "flavor_bitter": 0,
                    "flavor_strong": 0,
                },
            ]
        )
        # Sweet: (0*60 + 10*30) / 90 = 3.33 → 3
        # Sour: (0*60 + 8*30) / 90 = 2.67 → 3
        # Bitter: 0
        # Strong: (10*60 + 0*30) / 90 = 6.67 → 7
        assert profile["sweet"] == 3
        assert profile["sour"] == 3
        assert profile["bitter"] == 0
        assert profile["strong"] == 7

    def test_empty_list(self) -> None:
        profile = compute_flavor_profile([])
        assert profile == {"sweet": 0, "sour": 0, "bitter": 0, "strong": 0}

    def test_clamped_to_10(self) -> None:
        # Even if raw values are high, result is clamped to 10
        profile = compute_flavor_profile(
            [
                {
                    "measure": "1 oz",
                    "flavor_sweet": 10,
                    "flavor_sour": 10,
                    "flavor_bitter": 10,
                    "flavor_strong": 10,
                },
            ]
        )
        assert profile == {"sweet": 10, "sour": 10, "bitter": 10, "strong": 10}

    def test_missing_flavors(self) -> None:
        # Missing flavor keys default to 0
        profile = compute_flavor_profile([{"measure": "1 oz"}])
        assert profile == {"sweet": 0, "sour": 0, "bitter": 0, "strong": 0}


# ---------------------------------------------------------------------------
# compute_difficulty
# ---------------------------------------------------------------------------


class TestComputeDifficulty:
    def test_easy(self) -> None:
        assert compute_difficulty(2) == "easy"
        assert compute_difficulty(3, ["shaking"]) == "easy"

    def test_medium_by_count(self) -> None:
        assert compute_difficulty(4) == "medium"
        assert compute_difficulty(5) == "medium"

    def test_medium_by_techniques(self) -> None:
        assert compute_difficulty(2, ["shaking", "stirring"]) == "medium"

    def test_hard_by_count(self) -> None:
        assert compute_difficulty(6) == "hard"
        assert compute_difficulty(10) == "hard"

    def test_hard_by_technique(self) -> None:
        assert compute_difficulty(2, ["muddling"]) == "hard"
        assert compute_difficulty(3, ["layering"]) == "hard"
        assert compute_difficulty(1, ["flaming"]) == "hard"

    @pytest.mark.parametrize(
        "technique",
        ["muddling", "layering", "smoking", "flaming", "sous vide", "fat-washing", "infusing"],
    )
    def test_all_hard_techniques(self, technique: str) -> None:
        assert compute_difficulty(1, [technique]) == "hard"

    def test_none_techniques(self) -> None:
        assert compute_difficulty(3) == "easy"

    def test_case_insensitive(self) -> None:
        assert compute_difficulty(2, ["MUDDLING"]) == "hard"
        assert compute_difficulty(2, ["Layering"]) == "hard"
