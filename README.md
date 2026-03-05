# cocktailfyi

Cocktail computation engine for developers — measure parsing, ABV estimation, calorie calculation, flavor profiling, and difficulty scoring. Zero dependencies. <1ms per computation.

Extracted from the [CocktailFYI](https://cocktailfyi.com) Django app as a standalone pure-Python library.

<p align="center">
  <img src="demo.gif" alt="cocktailfyi demo — cocktail engine and API usage" width="800">
</p>

## Install

```bash
pip install cocktailfyi          # Core engine (zero deps)
pip install cocktailfyi[cli]     # + CLI (typer, rich)
pip install cocktailfyi[mcp]     # + MCP server
pip install cocktailfyi[api]     # + API client (httpx)
pip install cocktailfyi[all]     # Everything
```

## Quick Start

```python
from cocktailfyi import parse_measure_ml, estimate_abv, estimate_calories

# Parse bartending measures
ml = parse_measure_ml("1 1/2 oz")   # 45.0
ml = parse_measure_ml("2 cl")       # 20.0
ml = parse_measure_ml("splash")     # 5.0

# Estimate ABV (with 22% dilution from ice)
abv = estimate_abv([
    {"measure": "2 oz", "abv": 40.0},    # Tequila
    {"measure": "1 oz", "abv": 40.0},    # Triple Sec
    {"measure": "1 oz", "abv": 0},       # Lime juice
])
print(abv)  # Decimal('20.80')

# Estimate calories
kcal = estimate_calories([
    {"measure": "2 oz", "abv": 40.0, "calories_per_100ml": None},
    {"measure": "1 oz", "abv": 0, "calories_per_100ml": 40},
])
print(kcal)  # 145
```

## Features

### Measure Parser

Handles 20 bartending units including fractions:

```python
from cocktailfyi import parse_measure_ml

parse_measure_ml("1 1/2 oz")  # 45.0
parse_measure_ml("3/4 cl")    # 7.5
parse_measure_ml("2 tbsp")    # 30.0
parse_measure_ml("1 jigger")  # 45.0
parse_measure_ml("garnish")   # 5.0 (descriptive measure)
```

Supported units: oz, cl, ml, tsp, tbsp, shot, cup, part/parts, dash/dashes, drop/drops, splash, jigger, pint, glass, can, bottle, fifth.

### ABV Estimation

```python
from cocktailfyi import estimate_abv

abv = estimate_abv([
    {"measure": "2 oz", "abv": 40.0},   # Spirit
    {"measure": "4 oz", "abv": 0},      # Mixer
])
# Applies 22% dilution factor → Decimal('10.40')
```

### Calorie Estimation

```python
from cocktailfyi import estimate_calories

kcal = estimate_calories([
    {"measure": "2 oz", "abv": 40.0, "calories_per_100ml": None},
])
# Uses alcohol formula: vol × abv × 0.789 g/ml × 7 kcal/g → 133
```

### Flavor Profiling

```python
from cocktailfyi import compute_flavor_profile

profile = compute_flavor_profile([
    {"measure": "2 oz", "flavor_sweet": 0, "flavor_sour": 0,
     "flavor_bitter": 0, "flavor_strong": 10},
    {"measure": "1 oz", "flavor_sweet": 10, "flavor_sour": 8,
     "flavor_bitter": 0, "flavor_strong": 0},
])
# {'sweet': 3, 'sour': 3, 'bitter': 0, 'strong': 7}
```

### Difficulty Scoring

```python
from cocktailfyi import compute_difficulty

compute_difficulty(3)                        # 'easy'
compute_difficulty(5, ["muddling"])          # 'hard'
compute_difficulty(4, ["shaking", "stirring"])  # 'medium'
```

## CLI

```bash
cocktailfyi parse-measure "1 1/2 oz"
cocktailfyi abv '[{"measure":"2 oz","abv":40}]'
cocktailfyi calories '[{"measure":"2 oz","abv":40}]'
cocktailfyi difficulty 5 --techniques muddling shaking
```

## MCP Server

```bash
# Add to Claude Desktop config
python -m cocktailfyi.mcp_server
```

Tools: `parse_measure`, `cocktail_abv`, `cocktail_calories`, `flavor_profile`, `cocktail_difficulty`

## API Client

```python
from cocktailfyi.api import CocktailFYI

with CocktailFYI() as api:
    results = api.search("margarita")
```

## Links

- [CocktailFYI](https://cocktailfyi.com) — 426 cocktail recipes with ABV, calories, and flavor data
- [PyPI](https://pypi.org/project/cocktailfyi/)
- [GitHub](https://github.com/fyipedia/cocktailfyi)
- [FYIPedia](https://fyipedia.com) — Open-source developer tools ecosystem
