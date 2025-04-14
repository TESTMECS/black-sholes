"""
Pydantic models for heatmaps.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any


class HeatmapBase(BaseModel):
    """Base heatmap model."""

    heatmap_type: str = Field(
        ..., description="Type of heatmap (e.g., 'call_price', 'put_price')"
    )
    min_spot: float = Field(..., gt=0)
    max_spot: float = Field(..., gt=0)
    min_vol: float = Field(..., gt=0)
    max_vol: float = Field(..., gt=0)
    spot_steps: int = Field(..., gt=0)
    vol_steps: int = Field(..., gt=0)
    heatmap_data: List[List[float]] = Field(
        ..., description="2D array of heatmap values"
    )


class HeatmapCreate(HeatmapBase):
    """Heatmap creation model."""

    pass


class HeatmapResponse(HeatmapBase):
    """Heatmap response model."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    calculation_id: int

    


class HeatmapList(BaseModel):
    """Heatmap list response model."""

    calculation_id: int
    heatmaps: Dict[str, Any]
