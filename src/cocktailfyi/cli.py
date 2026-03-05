"""Command-line interface for cocktailfyi.

Requires the ``cli`` extra: ``pip install cocktailfyi[cli]``

Usage::

    cocktailfyi parse-measure "1 1/2 oz"         # → 45.0 ml
    cocktailfyi abv '[{"measure":"2 oz","abv":40}]'  # → 20.80%
    cocktailfyi calories '[{"measure":"2 oz","abv":40}]'  # → 133 kcal
    cocktailfyi flavor '[{"measure":"2 oz","flavor_sweet":2,...}]'
    cocktailfyi difficulty 5 --techniques muddling shaking
"""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="cocktailfyi",
    help="Cocktail computation engine — ABV, calories, flavor profiles, measure parsing.",
    no_args_is_help=True,
)
console = Console()


@app.command("parse-measure")
def parse_measure(
    measure: str = typer.Argument(help="Measure string (e.g. '1 1/2 oz', '2 cl', 'splash')"),
) -> None:
    """Parse a cocktail measure string into milliliters."""
    from cocktailfyi import parse_measure_ml

    ml = parse_measure_ml(measure)

    table = Table(title=f"Measure: {measure}")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value")
    table.add_row("Input", measure)
    table.add_row("Milliliters", f"{ml:.1f} ml")
    table.add_row("Ounces", f"{ml / 30.0:.2f} oz")
    table.add_row("Centiliters", f"{ml / 10.0:.1f} cl")
    console.print(table)


@app.command()
def abv(
    ingredients_json: str = typer.Argument(
        help='JSON array of ingredients, e.g. \'[{"measure":"2 oz","abv":40}]\''
    ),
) -> None:
    """Estimate cocktail ABV from ingredients."""
    from cocktailfyi import estimate_abv

    ingredients = json.loads(ingredients_json)
    result = estimate_abv(ingredients)

    table = Table(title="ABV Estimation")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value")
    table.add_row("Ingredients", str(len(ingredients)))
    table.add_row("Estimated ABV", f"{result}%")
    table.add_row("Dilution factor", "22% (ice/shaking)")
    console.print(table)


@app.command()
def calories(
    ingredients_json: str = typer.Argument(
        help='JSON array of ingredients, e.g. \'[{"measure":"2 oz","abv":40}]\''
    ),
) -> None:
    """Estimate total calories for a cocktail."""
    from cocktailfyi import estimate_calories

    ingredients = json.loads(ingredients_json)
    result = estimate_calories(ingredients)

    table = Table(title="Calorie Estimation")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value")
    table.add_row("Ingredients", str(len(ingredients)))
    table.add_row("Estimated calories", f"{result} kcal")
    console.print(table)


@app.command()
def flavor(
    ingredients_json: str = typer.Argument(
        help="JSON array of ingredients with flavor_sweet/sour/bitter/strong (0-10)"
    ),
) -> None:
    """Compute weighted flavor profile for a cocktail."""
    from cocktailfyi import compute_flavor_profile

    ingredients = json.loads(ingredients_json)
    profile = compute_flavor_profile(ingredients)

    table = Table(title="Flavor Profile")
    table.add_column("Dimension", style="cyan", no_wrap=True)
    table.add_column("Score (0-10)")
    table.add_column("Bar")

    for key in ("sweet", "sour", "bitter", "strong"):
        val = profile[key]
        bar = "█" * val + "░" * (10 - val)
        table.add_row(key.capitalize(), str(val), bar)

    console.print(table)


@app.command()
def difficulty(
    ingredient_count: int = typer.Argument(help="Number of ingredients"),
    techniques: list[str] | None = typer.Option(  # noqa: B008
        None, "--techniques", "-t", help="Techniques used (e.g. muddling, layering)"
    ),
) -> None:
    """Compute difficulty level for a cocktail recipe."""
    from cocktailfyi import compute_difficulty

    level = compute_difficulty(ingredient_count, techniques)
    color = {"easy": "green", "medium": "yellow", "hard": "red"}[level]

    table = Table(title="Difficulty Assessment")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value")
    table.add_row("Ingredients", str(ingredient_count))
    table.add_row("Techniques", ", ".join(techniques) if techniques else "none")
    table.add_row("Difficulty", f"[{color}]{level.upper()}[/{color}]")
    console.print(table)


if __name__ == "__main__":
    app()
