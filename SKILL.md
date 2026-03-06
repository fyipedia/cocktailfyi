---
name: cocktail-tools
description: Parse bartending measures, estimate ABV and calories, compute flavor profiles, score recipe difficulty, and search 636 cocktail recipes. Use when working with cocktail recipes, drink calculations, or mixology data.
license: MIT
metadata:
  author: fyipedia
  version: "0.1.1"
  homepage: "https://cocktailfyi.com/"
---

# CocktailFYI -- Cocktail Tools for AI Agents

Pure Python cocktail computation engine plus API client. Parse bartending measures to milliliters, estimate ABV with dilution modeling, calculate calories, compute 4-dimension flavor profiles, and score recipe difficulty -- all with zero dependencies. Also includes an HTTP client for the CocktailFYI REST API (636 recipes, 15 families, 11 categories).

**Install**: `pip install cocktailfyi` (engine) or `pip install cocktailfyi[api]` (+ HTTP client) -- **Web**: [cocktailfyi.com](https://cocktailfyi.com/) -- **API**: [REST API](https://cocktailfyi.com/developers/) -- **PyPI**: [cocktailfyi](https://pypi.org/project/cocktailfyi/)

## When to Use

- User asks to convert bartending measures (oz, cl, dashes, jigger) to milliliters
- User needs ABV estimation for a cocktail recipe (with 22% ice dilution)
- User wants calorie estimation from ingredient list
- User asks about flavor profiles (sweet/sour/bitter/strong on 0-10 scale)
- User needs recipe difficulty scoring based on ingredients and techniques
- User wants to search cocktails, ingredients, or glossary terms

## Tools

### `parse_measure_ml(measure: str) -> float`

Parse any bartending measure string into milliliters. Supports 20 units and mixed fractions.

```python
from cocktailfyi import parse_measure_ml

parse_measure_ml("1 1/2 oz")  # 45.0
parse_measure_ml("2 cl")      # 20.0
parse_measure_ml("30 ml")     # 30.0
parse_measure_ml("1 tsp")     # 5.0
parse_measure_ml("splash")    # 5.0
parse_measure_ml("2 dashes")  # 2.0
parse_measure_ml("")           # 30.0 (default)
```

### `estimate_abv(ingredients: list[dict]) -> Decimal`

Estimate cocktail ABV from ingredient list. Applies 22% dilution factor (DILUTION_FACTOR = 0.78) from ice. Each dict needs `measure` (str) and `abv` (float).

```python
from cocktailfyi import estimate_abv

abv = estimate_abv([
    {"measure": "2 oz", "abv": 40.0},   # Tequila
    {"measure": "1 oz", "abv": 40.0},   # Triple Sec
    {"measure": "1 oz", "abv": 0},      # Lime juice
])
print(abv)  # Decimal('15.60')
```

### `estimate_calories(ingredients: list[dict]) -> int`

Estimate total calories. Each dict needs `measure` (str), `abv` (float|None), and `calories_per_100ml` (float|None). Falls back to alcohol calorie formula: `volume * (abv/100) * 0.789 g/ml * 7 kcal/g`.

```python
from cocktailfyi import estimate_calories

kcal = estimate_calories([
    {"measure": "2 oz", "abv": 40.0, "calories_per_100ml": None},
    {"measure": "1 oz", "abv": 0, "calories_per_100ml": 40},
])
print(kcal)  # 145
```

### `compute_flavor_profile(ingredients: list[dict]) -> dict[str, int]`

Volume-weighted average flavor profile on 0-10 scale. Each dict needs `measure` (str), `flavor_sweet`, `flavor_sour`, `flavor_bitter`, `flavor_strong` (int 0-10).

```python
from cocktailfyi import compute_flavor_profile

profile = compute_flavor_profile([
    {"measure": "2 oz", "flavor_sweet": 2, "flavor_sour": 0,
     "flavor_bitter": 0, "flavor_strong": 8},
    {"measure": "1 oz", "flavor_sweet": 8, "flavor_sour": 7,
     "flavor_bitter": 0, "flavor_strong": 0},
])
print(profile)  # {'sweet': 4, 'sour': 2, 'bitter': 0, 'strong': 5}
```

### `compute_difficulty(ingredient_count: int, techniques: list[str] | None = None) -> str`

Score recipe difficulty as "easy", "medium", or "hard". Hard techniques: muddling, layering, smoking, flaming, sous vide, fat-washing, infusing.

```python
from cocktailfyi import compute_difficulty

compute_difficulty(3, ["shaking"])      # 'easy'
compute_difficulty(4)                    # 'medium'
compute_difficulty(5, ["muddling"])     # 'hard'
compute_difficulty(7)                    # 'hard'
```

### `CocktailFYI` API Client

HTTP client for the cocktailfyi.com REST API. Requires `pip install cocktailfyi[api]`.

```python
from cocktailfyi.api import CocktailFYI

with CocktailFYI() as api:
    results = api.search("margarita")       # Search cocktails, ingredients, glossary
    term = api.glossary_term("muddling")    # Get glossary term by slug
    spec = api.openapi_spec()               # Get OpenAPI 3.1.0 spec
```

**Methods:**
- `search(query: str) -> dict` -- Search cocktails, ingredients, and glossary terms
- `glossary_term(slug: str) -> dict` -- Get a glossary term by slug
- `openapi_spec() -> dict` -- Get the OpenAPI specification

## REST API (No Auth Required)

```bash
# Search
curl "https://cocktailfyi.com/api/search/?q=margarita"

# Glossary term
curl "https://cocktailfyi.com/api/term/muddling/"
```

Full spec: [OpenAPI 3.1.0](https://cocktailfyi.com/api/openapi.json)

## Unit Conversion Reference

| Unit | ml | Unit | ml | Unit | ml |
|------|---:|------|---:|------|---:|
| oz | 30.0 | cl | 10.0 | ml | 1.0 |
| tsp | 5.0 | tbsp | 15.0 | shot | 45.0 |
| cup | 240.0 | jigger | 45.0 | pint | 473.0 |
| dash | 1.0 | drop | 0.5 | splash | 5.0 |
| part | 30.0 | glass | 240.0 | can | 355.0 |
| bottle | 750.0 | fifth | 750.0 | | |

## Cocktail Families

| Family | Template | Example |
|--------|----------|---------|
| Sour | Spirit + citrus + sweetener | Whiskey Sour, Margarita |
| Old Fashioned | Spirit + sugar + bitters | Old Fashioned, Sazerac |
| Martini | Spirit + aromatized wine | Dry Martini, Manhattan |
| Highball | Spirit + long mixer | Gin & Tonic, Cuba Libre |
| Fizz | Spirit + citrus + sweetener + soda | Gin Fizz |
| Collins | Spirit + citrus + sweetener + soda (tall) | Tom Collins |
| Daisy | Spirit + citrus + liqueur | Margarita, Sidecar |
| Flip | Spirit + whole egg + sweetener | Brandy Flip |
| Tiki | Rum(s) + citrus + syrups + spice | Mai Tai, Zombie |

## Constants

| Constant | Type | Description |
|----------|------|-------------|
| `UNIT_TO_ML` | `dict[str, float]` | 20 bartending units to ml |
| `DESCRIPTIVE_MEASURES` | `set[str]` | 16 descriptive measures (garnish, twist, etc.) |
| `HARD_TECHNIQUES` | `set[str]` | 7 advanced techniques triggering hard difficulty |
| `DILUTION_FACTOR` | `float` | 0.78 (22% dilution from ice) |

## Demo

![CocktailFYI demo](https://raw.githubusercontent.com/fyipedia/cocktailfyi/main/demo.gif)

## Beverage FYI Family

Part of the [FYIPedia](https://fyipedia.com) ecosystem: [CocktailFYI](https://cocktailfyi.com), [VinoFYI](https://vinofyi.com), [BeerFYI](https://beerfyi.com), [BrewFYI](https://brewfyi.com), [WhiskeyFYI](https://whiskeyfyi.com), [TeaFYI](https://teafyi.com), [NihonshuFYI](https://nihonshufyi.com).
