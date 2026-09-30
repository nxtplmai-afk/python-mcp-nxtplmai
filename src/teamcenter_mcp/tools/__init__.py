"""MCP tool registrations, grouped by Teamcenter domain."""

from fastmcp import FastMCP

from teamcenter_mcp.tools.datasets import register_dataset_tools
from teamcenter_mcp.tools.search import register_search_tools
from teamcenter_mcp.tools.workflow import register_workflow_tools


def register_all_tools(mcp: FastMCP) -> None:
    """Register every Teamcenter tool on the given server."""
    register_search_tools(mcp)
    register_dataset_tools(mcp)
    register_workflow_tools(mcp)
