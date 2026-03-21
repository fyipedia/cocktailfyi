"""MCP server for cocktailfyi — AI assistant tools for cocktailfyi.com.

Run: uvx --from "cocktailfyi[mcp]" python -m cocktailfyi.mcp_server
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CocktailFYI")


@mcp.tool()
def list_cocktails(limit: int = 20, offset: int = 0) -> str:
    """List cocktails from cocktailfyi.com.

    Args:
        limit: Maximum number of results. Default 20.
        offset: Number of results to skip. Default 0.
    """
    from cocktailfyi.api import CocktailFYI

    with CocktailFYI() as api:
        data = api.list_cocktails(limit=limit, offset=offset)
        results = data.get("results", data) if isinstance(data, dict) else data
        if not results:
            return "No cocktails found."
        items = results[:limit] if isinstance(results, list) else []
        return "\n".join(f"- {item.get('name', item.get('slug', '?'))}" for item in items)


@mcp.tool()
def get_cocktail(slug: str) -> str:
    """Get detailed information about a specific cocktail.

    Args:
        slug: URL slug identifier for the cocktail.
    """
    from cocktailfyi.api import CocktailFYI

    with CocktailFYI() as api:
        data = api.get_cocktail(slug)
        return str(data)


@mcp.tool()
def list_ingredients(limit: int = 20, offset: int = 0) -> str:
    """List ingredients from cocktailfyi.com.

    Args:
        limit: Maximum number of results. Default 20.
        offset: Number of results to skip. Default 0.
    """
    from cocktailfyi.api import CocktailFYI

    with CocktailFYI() as api:
        data = api.list_ingredients(limit=limit, offset=offset)
        results = data.get("results", data) if isinstance(data, dict) else data
        if not results:
            return "No ingredients found."
        items = results[:limit] if isinstance(results, list) else []
        return "\n".join(f"- {item.get('name', item.get('slug', '?'))}" for item in items)


@mcp.tool()
def search_cocktail(query: str) -> str:
    """Search cocktailfyi.com for cocktails, ingredients, and techniques.

    Args:
        query: Search query string.
    """
    from cocktailfyi.api import CocktailFYI

    with CocktailFYI() as api:
        data = api.search(query)
        results = data.get("results", data) if isinstance(data, dict) else data
        if not results:
            return f"No results found for \"{query}\"."
        items = results[:10] if isinstance(results, list) else []
        return "\n".join(f"- {item.get('name', item.get('slug', '?'))}" for item in items)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
