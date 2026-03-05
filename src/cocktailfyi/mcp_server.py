"""MCP server for cocktailfyi — cocktail computation tools for AI assistants.

Requires the ``mcp`` extra: ``pip install cocktailfyi[mcp]``

Run as a standalone server::

    python -m cocktailfyi.mcp_server

Or configure in ``claude_desktop_config.json``::

    {
        "mcpServers": {
            "cocktailfyi": {
                "command": "python",
                "args": ["-m", "cocktailfyi.mcp_server"]
            }
        }
    }
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cocktailfyi")


@mcp.tool()
def parse_measure(measure: str) -> str:
    """Parse a cocktail measure string into milliliters.

    Handles common bartending units: oz, cl, ml, tsp, tbsp, shot, cup,
    parts, dash, drop, splash, jigger, pint, glass, can, bottle, fifth.
    Also handles fractions like "1 1/2 oz".

    Args:
        measure: Measure string (e.g. "1 1/2 oz", "2 cl", "splash").
    """
    from cocktailfyi import parse_measure_ml

    ml = parse_measure_ml(measure)
    return "\n".join(
        [
            f"## Measure: {measure}",
            "",
            "| Unit | Value |",
            "|------|-------|",
            f"| Milliliters | {ml:.1f} ml |",
            f"| Ounces | {ml / 30.0:.2f} oz |",
            f"| Centiliters | {ml / 10.0:.1f} cl |",
        ]
    )


@mcp.tool()
def cocktail_abv(ingredients_json: str) -> str:
    """Estimate cocktail ABV (alcohol by volume) from ingredients.

    Applies ~22% dilution factor from ice/shaking.

    Args:
        ingredients_json: JSON array of ingredients. Each item needs
            "measure" (str) and "abv" (float, percentage).
            Example: '[{"measure":"2 oz","abv":40},{"measure":"1 oz","abv":0}]'
    """
    import json

    from cocktailfyi import estimate_abv

    ingredients = json.loads(ingredients_json)
    result = estimate_abv(ingredients)
    return f"Estimated ABV: **{result}%** (after 22% dilution from ice/shaking)"


@mcp.tool()
def cocktail_calories(ingredients_json: str) -> str:
    """Estimate total calories for a cocktail.

    Uses calories_per_100ml when available, falls back to alcohol calorie
    formula (volume * abv * 0.789 g/ml * 7 kcal/g).

    Args:
        ingredients_json: JSON array of ingredients. Each item needs
            "measure" (str), "abv" (float), and optionally "calories_per_100ml" (float).
            Example: '[{"measure":"2 oz","abv":40,"calories_per_100ml":null}]'
    """
    import json

    from cocktailfyi import estimate_calories

    ingredients = json.loads(ingredients_json)
    result = estimate_calories(ingredients)
    return f"Estimated calories: **{result} kcal**"


@mcp.tool()
def flavor_profile(ingredients_json: str) -> str:
    """Compute weighted flavor profile for a cocktail (0-10 scale).

    Weights each ingredient by volume. Returns sweet, sour, bitter, strong scores.

    Args:
        ingredients_json: JSON array of ingredients. Each item needs
            "measure" (str), "flavor_sweet" (int 0-10), "flavor_sour" (int 0-10),
            "flavor_bitter" (int 0-10), "flavor_strong" (int 0-10).
    """
    import json

    from cocktailfyi import compute_flavor_profile

    ingredients = json.loads(ingredients_json)
    profile = compute_flavor_profile(ingredients)
    lines = [
        "## Flavor Profile",
        "",
        "| Dimension | Score |",
        "|-----------|-------|",
    ]
    for key in ("sweet", "sour", "bitter", "strong"):
        val = profile[key]
        bar = "█" * val + "░" * (10 - val)
        lines.append(f"| {key.capitalize()} | {val}/10 {bar} |")
    return "\n".join(lines)


@mcp.tool()
def cocktail_difficulty(ingredient_count: int, techniques: str = "") -> str:
    """Compute difficulty level for a cocktail recipe.

    Rules: Hard (>=6 ingredients or hard technique), Medium (>=4 or >=2 techniques), Easy (else).
    Hard techniques: muddling, layering, smoking, flaming, sous vide, fat-washing, infusing.

    Args:
        ingredient_count: Number of ingredients in the recipe.
        techniques: Comma-separated technique names (e.g. "muddling,shaking").
    """
    from cocktailfyi import compute_difficulty

    tech_list = [t.strip() for t in techniques.split(",") if t.strip()] if techniques else []
    level = compute_difficulty(ingredient_count, tech_list)
    emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}[level]
    parts = f"{ingredient_count} ingredients, {len(tech_list)} techniques"
    return f"Difficulty: {emoji} **{level.upper()}** ({parts})"


if __name__ == "__main__":
    mcp.run()
