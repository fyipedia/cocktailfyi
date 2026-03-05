---
name: cocktail-tools
description: Look up cocktail recipes, calculate ABV and calories, analyze flavor profiles, and estimate difficulty from 636 cocktails and 489 ingredients.
---

# Cocktail Tools

Cocktail recipe analysis, ABV calculation, and flavor profiling powered by [cocktailfyi](https://cocktailfyi.com/) -- the complete cocktail reference covering 636 cocktails across 15 families.

## Setup

Install the MCP server:

```bash
pip install "cocktailfyi[mcp]"
```

Add to your `claude_desktop_config.json`:

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

## Available Tools

| Tool | Description |
|------|-------------|
| `parse_measure` | Parse cocktail measurements (oz, cl, ml, dash, barspoon) into standardized units |
| `cocktail_abv` | Calculate ABV for a cocktail from its ingredient list with volumes and spirits |
| `cocktail_calories` | Estimate calories from ingredients (alcohol, sugar, juice, mixers) |
| `flavor_profile` | Analyze flavor balance: sweet, sour, bitter, spirit-forward, effervescent |
| `cocktail_difficulty` | Estimate preparation difficulty from ingredient count and techniques |

## When to Use

- Calculating ABV or calories for a cocktail recipe
- Analyzing flavor profiles of custom drink recipes
- Parsing and converting cocktail measurements
- Estimating difficulty level for cocktail preparation
- Building cocktail menu tools or recipe analyzers

## Links

- [636 Cocktail Recipes](https://cocktailfyi.com/cocktails/)
- [489 Ingredients Database](https://cocktailfyi.com/ingredients/)
- [API Documentation](https://cocktailfyi.com/developers/)
- [PyPI Package](https://pypi.org/project/cocktailfyi/)
