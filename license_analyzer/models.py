from __future__ import annotations

import collections
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

Dependency = collections.namedtuple("Dependency", ["name", "extras", "specifier", "marker"])


class DistributionMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    version: str
    license: Annotated[Optional[str], Field(default=None)]
    license_classifiers: Annotated[list[str], Field(default=[])]
    author: Annotated[Optional[str], Field(default=None)]
    maintainer: Annotated[Optional[str], Field(default=None)]
    url: Annotated[Optional[str], Field(default=None)]
    description: Annotated[Optional[str], Field(default=None)]

    dependencies: Annotated[list[DistributionMetadata], Field(default=[])]


class DependencyGraph(BaseModel):
    distributions: Annotated[dict[str, DistributionMetadata], Field(default_factory=dict)]
