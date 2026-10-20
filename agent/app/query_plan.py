"""结构化查询计划（PRD §5 的 Query Plan）。"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Filter(BaseModel):
    field: str
    op: str = "="
    value: Any


class QueryPlan(BaseModel):
    dataset_id: int = 1
    metric: str
    dimensions: List[str] = Field(default_factory=list)
    filters: List[Filter] = Field(default_factory=list)
    time_range: Optional[str] = None
    sort: Optional[str] = None  # metric_desc | metric_asc | dimension_asc
    limit: int = 1000
