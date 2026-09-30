"""FastMCP server entry point for Teamcenter.

Run with ``python app.py`` after ``pip install -r requirements.txt``.
"""

import logging
import sys
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

# Make the ``teamcenter_mcp`` package under ./src importable without installing it.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from starlette.requests import Request
from starlette.responses import JSONResponse

from teamcenter_mcp import __version__
from teamcenter_mcp.client import TeamcenterClient
from teamcenter_mcp.config import get_settings
from teamcenter_mcp.tools import register_all_tools

logger = logging.getLogger(__name__)


@lifespan
async def teamcenter_lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Open one pooled Teamcenter HTTP client for the server's lifetime."""
    settings = get_settings()
    client = TeamcenterClient(settings.api_base_url, settings.teamcenter_http_timeout)
    logger.info("Teamcenter backend: %s", settings.api_base_url)
    try:
        yield {"teamcenter": client}
    finally:
        await client.aclose()


def create_server() -> FastMCP:
    """Build the FastMCP server with all Teamcenter tools registered."""
    mcp = FastMCP(
        name="teamcenter-mcp",
        version=__version__,
        instructions=(
            "Tools for searching Teamcenter Items, Item Revisions and Datasets, "
            "reading dataset content, and starting workflows. Dates use the "
            "Teamcenter format DD-MMM-YYYY HH:mm (e.g. 23-Aug-2026 13:10)."
        ),
        lifespan=teamcenter_lifespan,
    )
    register_all_tools(mcp)

    @mcp.custom_route("/health", methods=["GET"])
    async def health(request: Request) -> JSONResponse:
        """Liveness check for the HTTP transport (does not call the Teamcenter backend)."""
        return JSONResponse({"status": "ok", "server": "teamcenter-mcp", "version": __version__})

    return mcp


mcp = create_server()


def main() -> None:
    """Run the server using the transport configured in settings."""
    settings = get_settings()
    # Log to stderr so stdout stays clean for the stdio transport.
    logging.basicConfig(
        level=settings.log_level.upper(),
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if settings.mcp_transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport="http",
            host=settings.mcp_host,
            port=settings.mcp_port,
            path=settings.mcp_path,
        )


if __name__ == "__main__":
    main()
