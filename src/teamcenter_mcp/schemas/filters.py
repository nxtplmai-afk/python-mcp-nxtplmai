"""Search filter models for the Teamcenter saved queries.

Field names are snake_case for the MCP client. Each field's ``serialization_alias``
is the exact Teamcenter saved-query field name (e.g. ``"Item ID"``), so
:meth:`SearchFilters.to_criteria` produces the criteria dict the backend expects.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from teamcenter_mcp.schemas.common import tc_datetime_field

DatasetType = Literal["MSExcel", "MSExcelX", "PDF", "HTML"]


class SearchFilters(BaseModel):
    """Filters common to every Teamcenter search: ownership, release status and dates."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", serialize_by_alias=True)

    owning_user: str | None = Field(
        default=None,
        serialization_alias="Owning User",
        description="Teamcenter user ID of the owner. Example: infodba.",
    )
    owning_group: str | None = Field(
        default=None,
        serialization_alias="Owning Group",
        description="Owning Teamcenter group. Example: DBA, Engineering, Design.",
    )
    release_status: str | None = Field(
        default=None,
        serialization_alias="Release Status",
        description="Release status name. Example: Released, In Work, Approved, Obsolete.",
    )

    created_after: str | None = tc_datetime_field("Created After", "Only return objects created after this date/time.")
    created_before: str | None = tc_datetime_field("Created Before", "Only return objects created before this date/time.")
    modified_after: str | None = tc_datetime_field("Modified After", "Only return objects modified after this date/time.")
    modified_before: str | None = tc_datetime_field("Modified Before", "Only return objects modified before this date/time.")
    released_after: str | None = tc_datetime_field("Released After", "Only return objects released after this date/time.")
    released_before: str | None = tc_datetime_field("Released Before", "Only return objects released before this date/time.")

    def to_criteria(self) -> dict[str, str]:
        """Return only the filters that were set, keyed by Teamcenter field name."""
        return {key: value for key, value in self.model_dump(exclude_none=True).items() if value != ""}


class ItemSearchFilters(SearchFilters):
    """Filters for the ``Item...`` saved query."""

    name: str | None = Field(
        default=None,
        serialization_alias="Name",
        description="Item name. Wildcards (*) supported. Example: Motor*, TestPart*.",
    )
    item_id: str | None = Field(
        default=None,
        serialization_alias="Item ID",
        description="Unique Teamcenter Item ID. Example: 10001139311.",
    )
    description: str | None = Field(
        default=None,
        serialization_alias="Description",
        description="Item description text. Supports partial matching.",
    )
    type: str | None = Field(
        default=None,
        serialization_alias="Type",
        description="Teamcenter business object type. Example: Item, Part, Document.",
    )


class ItemRevisionSearchFilters(SearchFilters):
    """Filters for the ``Item Revision...`` saved query."""

    name: str | None = Field(
        default=None,
        serialization_alias="Name",
        description="Item Revision name. Wildcards (*) supported.",
    )
    item_id: str | None = Field(
        default=None,
        serialization_alias="Item ID",
        description="Item ID the revision belongs to.",
    )
    revision: str | None = Field(
        default=None,
        serialization_alias="Revision",
        description="Revision identifier, e.g. A, B, C.",
    )
    description: str | None = Field(
        default=None,
        serialization_alias="Description",
        description="Item Revision description.",
    )
    type: str | None = Field(
        default=None,
        serialization_alias="Type",
        description="Item Revision type. Example: ItemRevision, PartRevision, DocumentRevision.",
    )


class DatasetSearchFilters(SearchFilters):
    """Filters for the ``Dataset...`` saved query."""

    name: str | None = Field(
        default=None,
        serialization_alias="Name",
        description="Dataset name. Wildcards (*) supported. Example: Test*.pdf",
    )
    dataset_type: list[DatasetType] | None = Field(
        default=None,
        serialization_alias="Dataset Type",
        description="One or more dataset types. Example: ['PDF'] or ['PDF', 'HTML'].",
    )

    @field_serializer("dataset_type")
    def _join_dataset_types(self, value: list[DatasetType] | None) -> str | None:
        # Teamcenter saved queries accept multiple values as a comma-separated string.
        return ",".join(value) if value else None
