"""Dataset tools: list datasets attached to an Item and read dataset content."""

from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import Field

from teamcenter_mcp.client import get_client
from teamcenter_mcp.schemas import DatasetContentResponse, DatasetListResponse, NonBlankStr

READ_ONLY = {"readOnlyHint": True, "openWorldHint": True}


def register_dataset_tools(mcp: FastMCP) -> None:
    """Register ``getDatasetByItemId`` and ``readDataset``."""

    @mcp.tool(name="getDatasetByItemId", annotations=READ_ONLY)
    async def get_dataset_by_item_id(
        ctx: Context,
        item_id: Annotated[NonBlankStr, Field(description="Teamcenter Item ID used to retrieve related datasets.")],
    ) -> DatasetListResponse:
        """Retrieve datasets attached to a Teamcenter Item.

        Use this tool when a user:
        - Provides a Teamcenter Item ID.
        - Requests documents, PDFs, drawings, CAD files, or datasets related to an Item.
        - Wants datasets attached through Item Revisions.
        - Needs specification, reference, or rendering datasets for an Item.

        Returns: Dataset UID, Dataset Name and Relation Type for each dataset.

        Examples:
        - Get datasets for Item 006180
        - Show PDFs related to Item 006180

        Use this tool before readDataset when the user only knows the Item ID
        and does not yet have a Dataset UID.
        """
        datasets = await get_client(ctx).get_datasets_by_item_id(item_id)
        return DatasetListResponse(
            tool="getDatasetByItemId",
            item_id=item_id,
            dataset_count=len(datasets),
            datasets=datasets,
        )

    @mcp.tool(name="readDataset", annotations=READ_ONLY)
    async def read_dataset(
        ctx: Context,
        dataset_uid: Annotated[
            NonBlankStr,
            Field(description="Teamcenter Dataset UID returned by searchDatasets or getDatasetByItemId."),
        ],
    ) -> DatasetContentResponse:
        """Read content from a Teamcenter Dataset using its Dataset UID.

        The backend automatically refreshes the Dataset, loads the latest named
        references, resolves the current ImanFile, downloads the file from
        Teamcenter/FMS, and extracts its content.

        Supported formats: PDF, DOCX, XLSX/XLS, TXT, CSV, JSON, XML, HTML, MD, RTF.

        If the Dataset UID is unknown, first locate the dataset with
        searchDatasets or getDatasetByItemId, then call this tool with the
        returned UID.
        """
        content = await get_client(ctx).read_dataset(dataset_uid)
        return DatasetContentResponse(tool="readDataset", dataset_uid=dataset_uid, content=content)
