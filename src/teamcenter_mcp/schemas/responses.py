"""Tool response models.

Fields are snake_case in Python and serialized as camelCase (``resultCount``,
``datasetUid`` ...) to keep the response shape of the original JS server. Backend
payloads (search results, datasets, file content) are passed through untouched.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ToolResponse(BaseModel):
    """Base for all tool responses: camelCase on the wire, ``tool`` names the producer."""

    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, serialize_by_alias=True)

    tool: str


class SearchResponse(ToolResponse):
    """Result of a Teamcenter saved-query search."""

    query_name: str
    criteria: dict[str, str]
    result_count: int
    results: Any


class DatasetListResponse(ToolResponse):
    """Datasets attached to an Item."""

    item_id: str
    dataset_count: int
    datasets: list[Any]


class DatasetContentResponse(ToolResponse):
    """Extracted content of a dataset."""

    dataset_uid: str
    content: Any


class WorkflowResponse(ToolResponse):
    """Result of creating and starting a workflow."""

    item_id: str | None
    uid: str | None
    result: Any
