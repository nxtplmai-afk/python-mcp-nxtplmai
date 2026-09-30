"""Search tools: Items, Item Revisions and Datasets via Teamcenter saved queries."""

from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import Field

from teamcenter_mcp.client import count_results, get_client
from teamcenter_mcp.schemas import (
    DatasetSearchFilters,
    ItemRevisionSearchFilters,
    ItemSearchFilters,
    SearchFilters,
    SearchResponse,
)

ITEM_QUERY = "Item..."
ITEM_REVISION_QUERY = "Item Revision..."
DATASET_QUERY = "Dataset..."

READ_ONLY = {"readOnlyHint": True, "openWorldHint": True}


async def _run_search(ctx: Context, tool: str, query_name: str, filters: SearchFilters) -> SearchResponse:
    """Execute a saved query with the given filters and wrap the results."""
    criteria = filters.to_criteria()
    results = await get_client(ctx).search(query_name, criteria)
    return SearchResponse(
        tool=tool,
        query_name=query_name,
        criteria=criteria,
        result_count=count_results(results),
        results=results,
    )


def register_search_tools(mcp: FastMCP) -> None:
    """Register ``searchItems``, ``searchItemRevisions`` and ``searchDatasets``."""

    @mcp.tool(name="searchItems", annotations=READ_ONLY)
    async def search_items(
        ctx: Context,
        filters: Annotated[
            ItemSearchFilters,
            Field(default_factory=ItemSearchFilters, description="Item search filters. Only set the ones you need."),
        ],
    ) -> SearchResponse:
        """Search Teamcenter Items using metadata filters.

        Use this tool when:
        - Looking for Items in Teamcenter
        - Searching by Item ID, Name, Description or Type
        - Searching by Owning User or Group
        - Searching by Release Status
        - Filtering by Created, Modified or Released dates

        Returns: Item UID, Item ID, Item Name, Object Type, revision, ownership
        and release information.

        Examples:
        - Find Item 006180
        - Find all released Documents
        - Find Items owned by a specific user
        - Find Items modified after a given date
        """
        return await _run_search(ctx, "searchItems", ITEM_QUERY, filters)

    @mcp.tool(name="searchItemRevisions", annotations=READ_ONLY)
    async def search_item_revisions(
        ctx: Context,
        filters: Annotated[
            ItemRevisionSearchFilters,
            Field(
                default_factory=ItemRevisionSearchFilters,
                description="Item Revision search filters. Only set the ones you need.",
            ),
        ],
    ) -> SearchResponse:
        """Search Teamcenter Item Revisions using metadata filters.

        Use this tool when:
        - Looking for Item Revisions in Teamcenter
        - Searching by Item ID and Revision
        - Finding the latest or released revisions of an Item
        - Finding revisions owned by a specific user or group
        - Searching by revision name, description, or type
        - Filtering revisions by creation, modification, or release dates

        Returns: Revision UID, Item ID, Revision ID, Revision Name, Object Type,
        Owning User/Group, creation and modification dates, release information.

        Examples:
        - Find revision A of Item 006180
        - Find all revisions of Item 006180
        - Find released Item Revisions
        - Find Item Revisions modified after a specific date

        Use this tool whenever revision-level information is required rather
        than Item-level information.
        """
        return await _run_search(ctx, "searchItemRevisions", ITEM_REVISION_QUERY, filters)

    @mcp.tool(name="searchDatasets", annotations=READ_ONLY)
    async def search_datasets(
        ctx: Context,
        filters: Annotated[
            DatasetSearchFilters,
            Field(default_factory=DatasetSearchFilters, description="Dataset search filters. Only set the ones you need."),
        ],
    ) -> SearchResponse:
        """Search Teamcenter Datasets using metadata filters.

        Use this tool when:
        - Looking for PDF, Excel or HTML datasets
        - Searching by dataset name or type
        - Finding datasets owned by a specific user or group
        - Finding released datasets
        - Finding recently created or modified datasets

        Returns: Dataset UID, Name, Type, Owning User/Group, creation and
        modification dates, release information.

        Examples:
        - Find all PDF datasets
        - Find datasets named "Drawing"
        - Find released PDF documents
        - Find datasets created after a specified date

        To read a dataset's content, pass the returned Dataset UID to readDataset.
        """
        return await _run_search(ctx, "searchDatasets", DATASET_QUERY, filters)
