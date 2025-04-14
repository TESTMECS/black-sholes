"""
Pydantic models for calculations.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class CalculationBase(BaseModel):
    """Base calculation model."""

    spot_price: float = Field(..., gt=0)
    strike_price: float = Field(..., gt=0)
    time_to_maturity: float = Field(..., gt=0)
    volatility: float = Field(..., gt=0)
    risk_free_rate: float
    call_price: float = Field(..., ge=0)
    put_price: float = Field(..., ge=0)


class CalculationCreate(CalculationBase):
    """Calculation creation model."""

    pass


class CalculationResponse(CalculationBase):
    """Calculation response model."""

    id: int
    timestamp: str
    heatmaps: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class CalculationList(BaseModel):
    """Calculation list response model."""

    data: List[CalculationResponse]
    meta: Dict[str, Any]
