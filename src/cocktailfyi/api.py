"""HTTP API client for cocktailfyi.com REST endpoints.

Requires the ``api`` extra: ``pip install cocktailfyi[api]``

Usage::

    from cocktailfyi.api import CocktailFYI

    with CocktailFYI() as api:
        results = api.search("margarita")
        print(results)
"""

from __future__ import annotations

from typing import Any

import httpx


class CocktailFYI:
    """API client for the cocktailfyi.com REST API.

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

    # -- HTTP helpers ----------------------------------------------------------

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        resp = self._client.get(path, params={k: v for k, v in params.items() if v is not None})
        resp.raise_for_status()
        result: dict[str, Any] = resp.json()
        return result

    # -- Endpoints -------------------------------------------------------------

    def search(self, query: str) -> dict[str, Any]:
        """Search cocktails, ingredients, and glossary terms.

        Args:
            query: Search term (e.g. ``"margarita"``, ``"vodka"``).
        """
        return self._get("/api/search/", q=query)

    def glossary_term(self, slug: str) -> dict[str, Any]:
        """Get a glossary term by slug.

        Args:
            slug: Term slug (e.g. ``"muddling"``, ``"dry-shake"``).
        """
        return self._get(f"/api/term/{slug}/")

    def openapi_spec(self) -> dict[str, Any]:
        """Get the OpenAPI specification."""
        return self._get("/api/openapi.json")

    # -- Context manager -------------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP connection."""
        self._client.close()

    def __enter__(self) -> CocktailFYI:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
