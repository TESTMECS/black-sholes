"""
Calculation routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query

from api.models.calculations import (
    CalculationCreate,
    CalculationResponse,
    CalculationList,
)
from database.models.calculations import (
    get_calculations,
    get_calculation_by_id,
    store_calculation,
)
from api.auth import get_current_user

router = APIRouter(prefix="/api/calculations", tags=["calculations"])


@router.get("/", response_model=CalculationList)
async def list_calculations(
    current_user: str = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Get a list of calculations with pagination.

    Parameters
    ----------
    current_user : str
        Current authenticated user
    limit : int
        Maximum number of results to return (default: 100, max: 500)
    offset : int
        Number of results to skip (default: 0)

    Returns
    -------
    CalculationList
        List of calculations
    """
    calculations = get_calculations(limit=limit, offset=offset)
    return {
        "data": calculations,
        "meta": {"limit": limit, "offset": offset, "count": len(calculations)},
    }


@router.get("/{calculation_id}", response_model=CalculationResponse)
async def get_calculation(
    calculation_id: int, current_user: str = Depends(get_current_user)
):
    """
    Get a specific calculation by ID.

    Parameters
    ----------
    calculation_id : int
        ID of the calculation to retrieve
    current_user : str
        Current authenticated user

    Returns
    -------
    CalculationResponse
        Calculation data

    Raises
    ------
    HTTPException
        If the calculation is not found
    """
    try:
        calculation = get_calculation_by_id(calculation_id)
        if not calculation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Calculation with ID {calculation_id} not found",
            )
        return calculation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED
)
async def create_calculation(
    calculation: CalculationCreate, current_user: str = Depends(get_current_user)
):
    """
    Create a new calculation.

    Parameters
    ----------
    calculation : CalculationCreate
        Calculation data
    current_user : str
        Current authenticated user

    Returns
    -------
    CalculationResponse
        Created calculation data

    Raises
    ------
    HTTPException
        If there is an error creating the calculation
    """
    try:
        calculation_id = store_calculation(
            spot_price=calculation.spot_price,
            strike_price=calculation.strike_price,
            time_to_maturity=calculation.time_to_maturity,
            volatility=calculation.volatility,
            risk_free_rate=calculation.risk_free_rate,
            call_price=calculation.call_price,
            put_price=calculation.put_price,
        )

        # Return the newly created calculation
        return get_calculation_by_id(calculation_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
