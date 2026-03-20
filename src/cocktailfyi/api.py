"""HTTP API client for cocktailfyi.com REST endpoints.

Requires the ``api`` extra: ``pip install cocktailfyi[api]``

Usage::

    from cocktailfyi.api import CocktailFYI

    with CocktailFYI() as api:
        items = api.list_categories()
        detail = api.get_category("example-slug")
        results = api.search("query")
"""

from __future__ import annotations

from typing import Any

import httpx


class CocktailFYI:
    """API client for the cocktailfyi.com REST API.

    Provides typed access to all cocktailfyi.com endpoints including
    list, detail, and search operations.

    Args:
        base_url: API base URL. Defaults to ``https://cocktailfyi.com``.
        timeout: Request timeout in seconds. Defaults to ``10.0``.
    """

    def __init__(
        self,
        base_url: str = "https://cocktailfyi.com",
        timeout: float = 10.0,
    ) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        resp = self._client.get(
            path,
            params={k: v for k, v in params.items() if v is not None},
        )
        resp.raise_for_status()
        result: dict[str, Any] = resp.json()
        return result

    # -- Endpoints -----------------------------------------------------------

    def list_categories(self, **params: Any) -> dict[str, Any]:
        """List all categories."""
        return self._get("/api/v1/categories/", **params)

    def get_category(self, slug: str) -> dict[str, Any]:
        """Get category by slug."""
        return self._get(f"/api/v1/categories/" + slug + "/")

    def list_cocktails(self, **params: Any) -> dict[str, Any]:
        """List all cocktails."""
        return self._get("/api/v1/cocktails/", **params)

    def get_cocktail(self, slug: str) -> dict[str, Any]:
        """Get cocktail by slug."""
        return self._get(f"/api/v1/cocktails/" + slug + "/")

    def list_faqs(self, **params: Any) -> dict[str, Any]:
        """List all faqs."""
        return self._get("/api/v1/faqs/", **params)

    def get_faq(self, slug: str) -> dict[str, Any]:
        """Get faq by slug."""
        return self._get(f"/api/v1/faqs/" + slug + "/")

    def list_glossary(self, **params: Any) -> dict[str, Any]:
        """List all glossary."""
        return self._get("/api/v1/glossary/", **params)

    def get_term(self, slug: str) -> dict[str, Any]:
        """Get term by slug."""
        return self._get(f"/api/v1/glossary/" + slug + "/")

    def list_guides(self, **params: Any) -> dict[str, Any]:
        """List all guides."""
        return self._get("/api/v1/guides/", **params)

    def get_guide(self, slug: str) -> dict[str, Any]:
        """Get guide by slug."""
        return self._get(f"/api/v1/guides/" + slug + "/")

    def list_ingredients(self, **params: Any) -> dict[str, Any]:
        """List all ingredients."""
        return self._get("/api/v1/ingredients/", **params)

    def get_ingredient(self, slug: str) -> dict[str, Any]:
        """Get ingredient by slug."""
        return self._get(f"/api/v1/ingredients/" + slug + "/")

    def list_techniques(self, **params: Any) -> dict[str, Any]:
        """List all techniques."""
        return self._get("/api/v1/techniques/", **params)

    def get_technique(self, slug: str) -> dict[str, Any]:
        """Get technique by slug."""
        return self._get(f"/api/v1/techniques/" + slug + "/")

    def search(self, query: str, **params: Any) -> dict[str, Any]:
        """Search across all content."""
        return self._get(f"/api/v1/search/", q=query, **params)

    # -- Lifecycle -----------------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> CocktailFYI:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
