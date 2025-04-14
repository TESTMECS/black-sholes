"""
Heatmap routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from api.models.heatmaps import HeatmapCreate, HeatmapList
from database.models.heatmap import store_heatmap_data
from database.models.calculations import get_calculation_by_id
from api.auth import get_current_user

router = APIRouter(tags=["heatmaps"])


@router.get("/api/calculation/{calculation_id}/heatmaps", response_model=HeatmapList)
async def get_heatmaps(
    calculation_id: int, current_user: str = Depends(get_current_user)
):
    """
    Get all heatmaps for a specific calculation.

    Parameters
    ----------
    calculation_id : int
        ID of the calculation
    current_user : str
        Current authenticated user

    Returns
    -------
    HeatmapList
        List of heatmaps for the calculation

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

        # Extract heatmaps from the calculation response
        heatmaps = calculation.get("heatmaps", {})

        return {"calculation_id": calculation_id, "heatmaps": heatmaps}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/api/calculation/{calculation_id}/heatmaps",
    status_code=status.HTTP_201_CREATED,
)
async def add_heatmap(
    calculation_id: int,
    heatmap: HeatmapCreate,
    current_user: str = Depends(get_current_user),
):
    """
    Add a new heatmap to a calculation.

    Parameters
    ----------
    calculation_id : int
        ID of the calculation
    heatmap : HeatmapCreate
        Heatmap data
    current_user : str
        Current authenticated user

    Returns
    -------
    dict
        Success message

    Raises
    ------
    HTTPException
        If there is an error adding the heatmap
    """
    try:
        # Check if calculation exists
        calculation = get_calculation_by_id(calculation_id)
        if not calculation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Calculation with ID {calculation_id} not found",
            )

        # Store the heatmap
        heatmap_id = store_heatmap_data(
            calculation_id=calculation_id,
            heatmap_type=heatmap.heatmap_type,
            min_spot=heatmap.min_spot,
            max_spot=heatmap.max_spot,
            min_vol=heatmap.min_vol,
            max_vol=heatmap.max_vol,
            spot_steps=heatmap.spot_steps,
            vol_steps=heatmap.vol_steps,
            heatmap_data=heatmap.heatmap_data,
        )

        return {
            "message": "Heatmap added successfully",
            "heatmap_id": heatmap_id,
            "calculation_id": calculation_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
