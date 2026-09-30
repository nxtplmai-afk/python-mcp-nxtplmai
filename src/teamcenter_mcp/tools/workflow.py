"""Workflow tools: start Teamcenter workflows on Items / Item Revisions."""

from typing import Annotated

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from teamcenter_mcp.client import get_client
from teamcenter_mcp.schemas import WorkflowResponse


def register_workflow_tools(mcp: FastMCP) -> None:
    """Register ``initiateWorkflow``."""

    @mcp.tool(
        name="initiateWorkflow",
        # Starts a real workflow in Teamcenter: not read-only and not safe to repeat.
        annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
    )
    async def initiate_workflow(
        ctx: Context,
        item_id: Annotated[str | None, Field(description="Teamcenter Item ID, if available.")] = None,
        uid: Annotated[str | None, Field(description="Teamcenter Item Revision UID, if available (Item Revision UIDs only).")] = None,
    ) -> WorkflowResponse:
        """Create and start a Teamcenter workflow.

        Use this tool when a user wants to:
        - Start a workflow for a Teamcenter Item.
        - Release an Item.
        - Submit an Item for approval.

        Provide item_id and/or uid; at least one is required.

        The backend automatically:
        - Uses item_id when provided, otherwise uid.
        - Finds the latest Item Revision from the Item ID when required.
        - Builds the workflow name, attaches the revision and starts the workflow.
        """
        item_id = (item_id or "").strip() or None
        uid = (uid or "").strip() or None
        if item_id is None and uid is None:
            raise ToolError("Either item_id or uid must be provided")

        result = await get_client(ctx).create_workflow(item_id, uid)
        return WorkflowResponse(tool="initiateWorkflow", item_id=item_id, uid=uid, result=result)
