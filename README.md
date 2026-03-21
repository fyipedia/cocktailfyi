# cocktailfyi

[![PyPI version](https://agentgif.com/badge/pypi/cocktailfyi/version.svg)](https://pypi.org/project/cocktailfyi/)
[![Python](https://img.shields.io/pypi/pyversions/cocktailfyi)](https://pypi.org/project/cocktailfyi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)](https://pypi.org/project/cocktailfyi/)

Cocktail computation engine for developers -- measure parsing, ABV estimation, calorie calculation, flavor profiling, and difficulty scoring. Pure Python, zero dependencies, sub-millisecond per computation. Extracted from the [CocktailFYI](https://cocktailfyi.com) cocktail database of 636 recipes across 15 families and 11 categories.

> **Try the interactive tools at [cocktailfyi.com](https://cocktailfyi.com)** -- , , [Cocktail Explorer](https://cocktailfyi.com/categories/) , [Ingredient Guide](https://cocktailfyi.com/ingredients/)

<p align="center">
  <img src="https://raw.githubusercontent.com/fyipedia/cocktailfyi/main/demo.gif" alt="cocktailfyi demo — cocktail engine and API usage" width="800">
</p>

## Table of Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [What You Can Do](#what-you-can-do)
  - [Parse Bartending Measures](#parse-bartending-measures)
  - [Estimate ABV (Alcohol by Volume)](#estimate-abv-alcohol-by-volume)
  - [Estimate Calories](#estimate-calories)
  - [Compute Flavor Profiles](#compute-flavor-profiles)
  - [Score Recipe Difficulty](#score-recipe-difficulty)
  - [Cocktail Families](#cocktail-families)
  - [ABV & Nutrition Science](#abv--nutrition-science)
  - [Flavor Profile Dimensions](#flavor-profile-dimensions)
- [Command-Line Interface](#command-line-interface)
- [MCP Server (Claude, Cursor, Windsurf)](#mcp-server-claude-cursor-windsurf)
- [REST API Client](#rest-api-client)
- [API Reference](#api-reference)
- [Learn More About Cocktails](#learn-more-about-cocktails)
- [Beverage FYI Family](#beverage-fyi-family)
- [License](#license)

## Install

```bash
pip install cocktailfyi          # Core engine (zero deps)
pip install cocktailfyi[cli]     # + CLI (typer, rich)
pip install cocktailfyi[mcp]     # + MCP server
pip install cocktailfyi[api]     # + API client (httpx)
pip install cocktailfyi[all]     # Everything
```

Requires Python 3.10+. The core engine has **zero dependencies** -- only extras add libraries.

## Quick Start

```python
from cocktailfyi import parse_measure_ml, estimate_abv, estimate_calories

# Parse bartending measures into milliliters
ml = parse_measure_ml("1 1/2 oz")   # 45.0
ml = parse_measure_ml("2 cl")       # 20.0
ml = parse_measure_ml("splash")     # 5.0

# Estimate ABV for a Margarita (with 22% dilution from ice)
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

## What You Can Do

### Parse Bartending Measures

Convert any bartending measure string into milliliters. Handles 20 units including imperial, metric, and descriptive measures, with full fraction support (`1 1/2`, `3/4`).

| Unit | ml | Unit | ml | Unit | ml |
|------|---:|------|---:|------|---:|
| oz | 30.0 | cl | 10.0 | ml | 1.0 |
| tsp | 5.0 | tbsp | 15.0 | shot | 45.0 |
| cup | 240.0 | jigger | 45.0 | pint | 473.0 |
| dash | 1.0 | drop | 0.5 | splash | 5.0 |
| part | 30.0 | glass | 240.0 | can | 355.0 |
| bottle | 750.0 | fifth | 750.0 | | |

Descriptive measures like `garnish`, `twist`, `wedge`, `sprig`, `float`, and `pinch` are recognized and mapped to 5.0 ml (negligible volume).

```python
from cocktailfyi import parse_measure_ml

parse_measure_ml("1 1/2 oz")  # 45.0  — standard jigger
parse_measure_ml("3/4 cl")    # 7.5   — metric fraction
parse_measure_ml("2 tbsp")    # 30.0  — tablespoon
parse_measure_ml("1 jigger")  # 45.0  — barware unit
parse_measure_ml("garnish")   # 5.0   — descriptive measure
parse_measure_ml("2 dashes")  # 2.0   — bitters
```

Learn more: [Ingredient Guide](https://cocktailfyi.com/ingredients/) | [Glossary](https://cocktailfyi.com/glossary/)

### Estimate ABV (Alcohol by Volume)

Calculate the estimated ABV of a cocktail from its ingredient list. The engine applies a **22% dilution factor** to account for ice melt during shaking or stirring -- the standard assumption in professional bartending.

The dilution model: when a cocktail is shaken or stirred with ice, approximately 22% of the final volume is water from melted ice. This dilutes the alcohol concentration by a factor of 0.78 (i.e., `raw_abv * 0.78 = diluted_abv`).

```python
from cocktailfyi import estimate_abv

# Classic Margarita
abv = estimate_abv([
    {"measure": "2 oz", "abv": 40.0},   # Tequila
    {"measure": "1 oz", "abv": 40.0},   # Triple Sec
    {"measure": "1 oz", "abv": 0},      # Lime juice
])
print(abv)  # Decimal('15.60')

# Highball (lighter drink)
abv = estimate_abv([
    {"measure": "2 oz", "abv": 40.0},   # Spirit
    {"measure": "4 oz", "abv": 0},      # Mixer
])
print(abv)  # Decimal('10.40')
```

Learn more: | ### Estimate Calories

Estimate total calories for a cocktail. When `calories_per_100ml` data is available, it uses that directly. For spirit-only ingredients without calorie data, it falls back to the **alcohol calorie formula**:

```
calories = volume_ml x (abv / 100) x 0.789 g/ml x 7 kcal/g
```

This formula uses the density of ethanol (0.789 g/ml) and the caloric value of alcohol (7 kcal per gram) -- the standard method used by nutritional science for estimating alcohol-derived calories.

```python
from cocktailfyi import estimate_calories

# Spirit with known calorie data for mixer
kcal = estimate_calories([
    {"measure": "2 oz", "abv": 40.0, "calories_per_100ml": None},   # Gin (formula)
    {"measure": "1 oz", "abv": 0, "calories_per_100ml": 40},        # Tonic (known)
])
print(kcal)  # 145

# Pure spirit (formula only)
kcal = estimate_calories([
    {"measure": "2 oz", "abv": 40.0, "calories_per_100ml": None},
])
print(kcal)  # 133
```

Learn more: | [Guides](https://cocktailfyi.com/guide/)

### Compute Flavor Profiles

Generate a weighted-average flavor profile across 4 dimensions on a 0--10 scale. Each ingredient contributes proportionally to its volume in the final drink.

| Dimension | What it measures | High scorers |
|-----------|-----------------|--------------|
| Sweet | Sweetness intensity | Liqueurs, syrups, fruit juices |
| Sour | Acidity / tartness | Citrus juice, vinegar shrubs |
| Bitter | Bitterness level | Bitters, amari, Campari |
| Strong | Alcohol presence | Neat spirits, high-proof cocktails |

```python
from cocktailfyi import compute_flavor_profile

# Whiskey Sour profile
profile = compute_flavor_profile([
    {"measure": "2 oz", "flavor_sweet": 0, "flavor_sour": 0,
     "flavor_bitter": 0, "flavor_strong": 10},   # Bourbon
    {"measure": "1 oz", "flavor_sweet": 10, "flavor_sour": 8,
     "flavor_bitter": 0, "flavor_strong": 0},     # Lemon + syrup
])
print(profile)
# {'sweet': 3, 'sour': 3, 'bitter': 0, 'strong': 7}
```

The 15 cocktail families on CocktailFYI each have distinctive flavor signatures -- Sours lean sour/sweet, Old Fashioneds are strong/bitter, Fizzes are light/sweet, and Tiki drinks are sweet/sour with tropical complexity.

Learn more: | ### Score Recipe Difficulty

Evaluate how difficult a cocktail recipe is to prepare based on ingredient count and techniques used.

| Level | Criteria |
|-------|----------|
| Easy | Fewer than 4 ingredients, 0--1 simple techniques |
| Medium | 4--5 ingredients OR 2+ techniques |
| Hard | 6+ ingredients OR any advanced technique |

Advanced techniques that automatically trigger "hard" difficulty:

| Technique | Description |
|-----------|-------------|
| Muddling | Crushing herbs/fruit in the glass |
| Layering | Floating liquids by density |
| Smoking | Adding wood smoke flavor |
| Flaming | Igniting spirits for caramelization |
| Sous vide | Precision temperature infusion |
| Fat-washing | Infusing spirits with rendered fat |
| Infusing | Steeping flavors over time |

```python
from cocktailfyi import compute_difficulty

compute_difficulty(3)                              # 'easy'  — simple 3-ingredient drink
compute_difficulty(4, ["shaking", "stirring"])      # 'medium' — 4 ingredients, 2 techniques
compute_difficulty(5, ["muddling"])                 # 'hard'  — muddling is advanced
compute_difficulty(7)                               # 'hard'  — 7 ingredients
```

Learn more: [Cocktail Explorer](https://cocktailfyi.com/categories/) | [Technique Glossary](https://cocktailfyi.com/glossary/)

### Cocktail Families

Cocktails are organized into families based on their structural recipe pattern rather than ingredients. A family defines the ratio template -- for example, a Sour is always a spirit + citrus + sweetener. Understanding families helps bartenders improvise: swap the spirit in a Sour template and you get a different drink with the same balance.

| Family | Template | Classic Example | Flavor Signature |
|--------|----------|----------------|-----------------|
| Sour | Spirit + citrus + sweetener | Whiskey Sour, Margarita | Tart, balanced |
| Old Fashioned | Spirit + sugar + bitters | Old Fashioned, Sazerac | Strong, spirit-forward |
| Martini | Spirit + aromatized wine | Dry Martini, Manhattan | Clean, strong |
| Highball | Spirit + long mixer | Gin & Tonic, Cuba Libre | Light, refreshing |
| Fizz | Spirit + citrus + sweetener + soda | Gin Fizz, Ramos Gin Fizz | Effervescent, light |
| Collins | Spirit + citrus + sweetener + soda (tall) | Tom Collins, John Collins | Tall, easy-drinking |
| Daisy | Spirit + citrus + liqueur | Margarita, Sidecar | Fruity, balanced |
| Flip | Spirit + whole egg + sweetener | Brandy Flip, Coffee Flip | Creamy, rich |
| Julep | Spirit + sugar + mint (crushed ice) | Mint Julep | Herbaceous, cold |
| Smash | Spirit + sugar + herb + citrus | Whiskey Smash | Muddled, fresh |
| Swizzle | Spirit + citrus + sweetener (swizzled) | Queen's Park Swizzle | Tropical, frothy |
| Toddy | Spirit + sweetener + hot water | Hot Toddy | Warm, soothing |
| Punch | Spirit + citrus + sweetener + tea/spice | Planter's Punch | Batch, communal |
| Tiki | Rum(s) + citrus + syrups + spice | Mai Tai, Zombie | Complex, tropical |
| Ancestral | Spirit + sweetener + bitters (no citrus) | Sazerac, Vieux Carre | Bold, aromatic |

```python
from cocktailfyi import estimate_abv, compute_flavor_profile

# A Sour family cocktail -- spirit + citrus + sweetener
whiskey_sour = [
    {"measure": "2 oz", "abv": 40.0},   # Bourbon (the spirit)
    {"measure": "1 oz", "abv": 0},      # Lemon juice (the citrus)
    {"measure": "3/4 oz", "abv": 0},    # Simple syrup (the sweetener)
]
abv = estimate_abv(whiskey_sour)  # ABV with 22% dilution from ice
```

Learn more: | [Browse All Categories](https://cocktailfyi.com/categories/) | [Cocktail Database](https://cocktailfyi.com/)

### ABV & Nutrition Science

Alcohol by Volume (ABV) measures the percentage of pure ethanol in a liquid. For mixed drinks, ABV depends on the volume and strength of each ingredient plus dilution from ice. The standard dilution assumption in professional bartending is 22% -- meaning roughly one-fifth of the final drink volume is water from melted ice.

| Drink Style | Typical ABV | Dilution Source |
|-------------|------------|----------------|
| Neat spirit (no ice) | 40--46% | None |
| Spirit on the rocks | 25--30% | Melting ice over time |
| Stirred cocktail | 22--28% | 15--20% dilution (less vigorous) |
| Shaken cocktail | 15--22% | 22--25% dilution (ice shatters) |
| Highball (spirit + mixer) | 8--12% | Long mixer volume |
| Beer/wine cocktail | 4--8% | Low-ABV base |

The calorie calculation uses two methods depending on available data. For spirits without specific calorie data, the **alcohol calorie formula** derives calories from ethanol content: `volume x (ABV/100) x 0.789 g/ml x 7 kcal/g`. The 7 kcal/g figure is the caloric density of ethanol (compared to 4 kcal/g for carbohydrates and 9 kcal/g for fat).

```python
from cocktailfyi import estimate_abv, estimate_calories

# Compare ABV across drink styles
neat = estimate_abv([{"measure": "2 oz", "abv": 40.0}])           # Spirit-forward
highball = estimate_abv([
    {"measure": "2 oz", "abv": 40.0},
    {"measure": "4 oz", "abv": 0},    # Mixer dilutes the ABV significantly
])

# Calorie estimation -- formula vs known data
kcal = estimate_calories([
    {"measure": "2 oz", "abv": 40.0, "calories_per_100ml": None},  # Ethanol formula
    {"measure": "1 oz", "abv": 0, "calories_per_100ml": 40},       # Known calorie data
])
```

Learn more: | | [Guides](https://cocktailfyi.com/guide/)

### Flavor Profile Dimensions

The flavor profile system scores cocktails across 4 dimensions on a 0--10 scale, using volume-weighted averages of each ingredient's contribution. This quantitative approach enables programmatic cocktail comparison, recommendation engines, and data-driven recipe development.

| Dimension | Scale | Low (0--3) | Medium (4--6) | High (7--10) |
|-----------|-------|-----------|---------------|-------------|
| Sweet | Sweetness intensity | Dry Martini, Negroni | Daiquiri, Cosmopolitan | Pina Colada, Mudslide |
| Sour | Acidity / tartness | Old Fashioned, Manhattan | Whiskey Sour | Lemon Drop, Caipirinha |
| Bitter | Bitterness level | Mojito, Margarita | Aperol Spritz | Negroni, Campari Soda |
| Strong | Alcohol presence | Mimosa, Bellini | Gimlet, Daiquiri | Martini, Manhattan |

```python
from cocktailfyi import compute_flavor_profile

# Compare flavor profiles of different cocktail styles
negroni = compute_flavor_profile([
    {"measure": "1 oz", "flavor_sweet": 2, "flavor_sour": 0,
     "flavor_bitter": 8, "flavor_strong": 8},   # Gin
    {"measure": "1 oz", "flavor_sweet": 7, "flavor_sour": 1,
     "flavor_bitter": 9, "flavor_strong": 4},    # Campari
    {"measure": "1 oz", "flavor_sweet": 8, "flavor_sour": 0,
     "flavor_bitter": 3, "flavor_strong": 3},    # Sweet Vermouth
])
# Result: balanced bitter-sweet with strong alcohol presence
```

Learn more: | | ## Command-Line Interface

Requires the `cli` extra: `pip install cocktailfyi[cli]`

```bash
# Parse a bartending measure to milliliters
cocktailfyi parse-measure "1 1/2 oz"

# Estimate ABV for a cocktail
cocktailfyi abv '[{"measure":"2 oz","abv":40},{"measure":"1 oz","abv":0}]'

# Estimate calories
cocktailfyi calories '[{"measure":"2 oz","abv":40,"calories_per_100ml":null}]'

# Compute flavor profile
cocktailfyi flavor '[{"measure":"2 oz","flavor_sweet":2,"flavor_sour":0,"flavor_bitter":0,"flavor_strong":8}]'

# Score difficulty
cocktailfyi difficulty 5 --techniques muddling shaking
```

All commands output Rich-formatted tables with color-coded results.

## MCP Server (Claude, Cursor, Windsurf)

Requires the `mcp` extra: `pip install cocktailfyi[mcp]`

Add to your AI assistant's MCP configuration:

**Claude Desktop** (`claude_desktop_config.json`):

```json
{
    "mcpServers": {
        "cocktailfyi": {
            "command": "python",
            "args": ["-m", "cocktailfyi.mcp_server"]
        }
    }
}
```

**Cursor** (`.cursor/mcp.json`) and **Windsurf** (`~/.codeium/windsurf/mcp_config.json`) use the same format.

Available MCP tools:

| Tool | Description |
|------|-------------|
| `parse_measure` | Parse bartending measure to ml/oz/cl |
| `cocktail_abv` | Estimate ABV with dilution factor |
| `cocktail_calories` | Estimate calories from ingredients |
| `flavor_profile` | Compute 4-dimension flavor profile |
| `cocktail_difficulty` | Score recipe difficulty level |

Or use all 5 tools through the unified [fyipedia-mcp](https://github.com/fyipedia/fyipedia-mcp) hub (53 tools from 10 packages in one server).

## REST API Client

Requires the `api` extra: `pip install cocktailfyi[api]`

```python
from cocktailfyi.api import CocktailFYI

with CocktailFYI() as api:
    # Search cocktails, ingredients, glossary
    results = api.search("margarita")

    # Look up a glossary term
    term = api.glossary_term("muddling")

    # Get the OpenAPI spec
    spec = api.openapi_spec()
```

The full REST API at [cocktailfyi.com/developers/](https://cocktailfyi.com/developers/) provides 10 endpoints for cocktail data, ingredients, families, techniques, and search. [OpenAPI 3.1.0 spec](https://cocktailfyi.com/api/openapi.json).

## API Reference

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `parse_measure_ml(measure)` | `str` | `float` | Parse bartending measure to milliliters |
| `estimate_abv(ingredients)` | `list[dict]` | `Decimal` | Estimate ABV with 22% dilution |
| `estimate_calories(ingredients)` | `list[dict]` | `int` | Estimate total calories |
| `compute_flavor_profile(ingredients)` | `list[dict]` | `dict[str, int]` | Weighted flavor scores (0--10) |
| `compute_difficulty(count, techniques)` | `int`, `list[str]` | `str` | Difficulty: easy/medium/hard |

**Constants:**

| Constant | Type | Description |
|----------|------|-------------|
| `UNIT_TO_ML` | `dict[str, float]` | 20 bartending units to ml conversion |
| `DESCRIPTIVE_MEASURES` | `set[str]` | 16 descriptive measures (garnish, twist, etc.) |
| `HARD_TECHNIQUES` | `set[str]` | 7 advanced techniques that trigger hard difficulty |
| `DILUTION_FACTOR` | `float` | 0.78 (22% dilution from ice) |

## Learn More About Cocktails

- **Browse**: [Cocktail Database](https://cocktailfyi.com/) | | [Ingredients](https://cocktailfyi.com/ingredients/) | [Categories](https://cocktailfyi.com/categories/)
- **Tools**: | - **Guides**: [Glossary](https://cocktailfyi.com/glossary/) | [Guides](https://cocktailfyi.com/guide/) | - **API**: [REST API Docs](https://cocktailfyi.com/developers/) | [OpenAPI Spec](https://cocktailfyi.com/api/openapi.json)

## Beverage FYI Family

Part of the [FYIPedia](https://fyipedia.com) open-source developer tools ecosystem -- world beverages from cocktails to sake.

| Site | Domain | Focus |
|------|--------|-------|
| **CocktailFYI** | [cocktailfyi.com](https://cocktailfyi.com) | **636 cocktails, ABV, calories, flavor profiles** |
| VinoFYI | [vinofyi.com](https://vinofyi.com) | Wines, grapes, regions, wineries, food pairings |
| BeerFYI | [beerfyi.com](https://beerfyi.com) | 112 beer styles, hops, malts, yeast, BJCP |
| BrewFYI | [brewfyi.com](https://brewfyi.com) | 72 coffee varieties, roasting, 21 brew methods |
| WhiskeyFYI | [whiskeyfyi.com](https://whiskeyfyi.com) | 80 whiskey expressions, distilleries, regions |
| TeaFYI | [teafyi.com](https://teafyi.com) | 60 tea varieties, teaware, brewing guides |
| NihonshuFYI | [nihonshufyi.com](https://nihonshufyi.com) | 80 sake, rice varieties, 50 breweries |

## License

MIT
