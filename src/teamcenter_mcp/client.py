"""Async HTTP client for the Teamcenter REST backend.

A single :class:`TeamcenterClient` is created in the server lifespan and shared by
all tools, so connections are pooled instead of being opened per request.
"""

import json
import logging
from typing import Any
from urllib.parse import quote

import httpx
from fastmcp import Context
from fastmcp.exceptions import ToolError

logger = logging.getLogger(__name__)


class TeamcenterAPIError(ToolError):
    """A Teamcenter backend call failed.

    Subclasses ``ToolError`` so FastMCP reports the message to the MCP client
    as a tool error (``isError: true``) rather than masking it.
    """


def count_results(data: Any) -> int:
    """Count search hits whether the backend returned a list or ``{"results": [...]}``."""
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        return len(data["results"])
    return 0


class TeamcenterClient:
    """Thin async wrapper around the Teamcenter REST endpoints."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    async def aclose(self) -> None:
        """Close the underlying connection pool."""
        await self._http.aclose()

    async def _request(self, method: str, path: str, *, action: str, json_body: Any = None) -> Any:
        """Send a request and return the decoded JSON body.

        ``action`` is a human-readable description used in error messages,
        e.g. ``'execute Teamcenter query "Item..."'``.
        """
        logger.debug("%s %s body=%s", method, path, json_body)
        try:
            response = await self._http.request(method, path, json=json_body)
        except httpx.TimeoutException as exc:
            raise TeamcenterAPIError(f"Failed to {action}: request to Teamcenter timed out") from exc
        except httpx.HTTPError as exc:
            raise TeamcenterAPIError(f"Failed to {action}: {exc}") from exc

        if response.is_error:
            logger.error("Teamcenter %s %s failed (%s): %s", method, path, response.status_code, response.text)
            raise TeamcenterAPIError(
                f"Failed to {action}: Teamcenter API Error ({response.status_code}): {response.text}"
            )

        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise TeamcenterAPIError(f"Failed to {action}: backend returned a non-JSON response") from exc

    async def search(self, query_name: str, criteria: dict[str, str]) -> Any:
        """Run a saved Teamcenter query (``POST /api/search``)."""
        logger.info("Search %r criteria=%s", query_name, criteria)
        data = await self._request(
            "POST",
            "/api/search",
            action=f'execute Teamcenter query "{query_name}"',
            json_body={"queryName": query_name, "criteria": criteria},
        )
        logger.info("Search %r returned %d result(s)", query_name, count_results(data))
        return data

    async def get_datasets_by_item_id(self, item_id: str) -> list[Any]:
        """Return datasets attached to an Item (``GET /api/datasets/item/{itemId}``)."""
        data = await self._request(
            "GET",
            f"/api/datasets/item/{quote(item_id, safe='')}",
            action=f"retrieve datasets for Item ID {item_id}",
        )
        datasets = data.get("datasets") if isinstance(data, dict) else None
        return datasets or []

    async def read_dataset(self, dataset_uid: str) -> Any:
        """Download and extract a dataset's content (``GET /api/datasets/{uid}/content``)."""
        return await self._request(
            "GET",
            f"/api/datasets/{quote(dataset_uid, safe='')}/content",
            action=f"read dataset {dataset_uid}",
        )

    async def create_workflow(self, item_id: str | None, uid: str | None) -> Any:
        """Create and start a workflow (``POST /api/workflow/create``)."""
        logger.info("Create workflow itemId=%s uid=%s", item_id, uid)
        return await self._request(
            "POST",
            "/api/workflow/create",
            action="initiate Teamcenter workflow",
            json_body={"itemId": item_id, "uid": uid},
        )


def get_client(ctx: Context) -> TeamcenterClient:
    """Fetch the shared Teamcenter client created in the server lifespan."""
    return ctx.lifespan_context["teamcenter"]
