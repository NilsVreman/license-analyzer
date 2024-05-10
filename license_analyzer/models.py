from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class DistributionMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    version: str
    license: Optional[str] = None
    license_classifiers: list[str] = []
    author: Optional[str] = None
    maintainer: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None

    dependencies: Optional[list[DistributionMetadata]] = None
