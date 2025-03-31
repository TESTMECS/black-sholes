"""
SQLAlchemy ORM model for heatmap data.
"""

import json
import numpy as np
from typing import List, Dict, Any, Union, cast
from sqlalchemy import Column, Integer, Float, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker

from database.orm import Base, SessionLocal


class HeatmapData(Base):
    """SQLAlchemy model for heatmap_data table."""

    __tablename__ = "heatmap_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    calculation_id = Column(Integer, ForeignKey("calculations.id"), nullable=False)
    heatmap_type = Column(String, nullable=False)
    min_spot = Column(Float, nullable=False)
    max_spot = Column(Float, nullable=False)
    min_vol = Column(Float, nullable=False)
    max_vol = Column(Float, nullable=False)
    spot_steps = Column(Integer, nullable=False)
    vol_steps = Column(Integer, nullable=False)
    heatmap_json = Column(String, nullable=False)

    # Relationship with Calculation
    calculation = relationship("Calculation", back_populates="heatmaps")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "calculation_id": self.calculation_id,
            "heatmap_type": self.heatmap_type,
            "min_spot": self.min_spot,
            "max_spot": self.max_spot,
            "min_vol": self.min_vol,
            "max_vol": self.max_vol,
            "spot_steps": self.spot_steps,
            "vol_steps": self.vol_steps,
            "heatmap_json": self.heatmap_json,
        }


def store_heatmap_data(
    calculation_id: int,
    heatmap_type: str,
    min_spot: float,
    max_spot: float,
    min_vol: float,
    max_vol: float,
    spot_steps: int,
    vol_steps: int,
    heatmap_data: Union[np.ndarray, List[List[float]]],
    db_path: str = "instance/black_scholes.db",
) -> int:
    """
    Store heatmap data associated with a calculation.

    Parameters
    ----------
    calculation_id : int
        ID of the calculation this heatmap belongs to
    heatmap_type : str
        Type of heatmap (e.g., 'call_price', 'put_price', 'call_pnl', 'put_pnl')
    min_spot, max_spot : float
        Range of spot prices
    min_vol, max_vol : float
        Range of volatilities
    spot_steps, vol_steps : int
        Number of steps in the spot price and volatility grids
    heatmap_data : np.ndarray or List[List[float]]
        2D array of heatmap values
    db_path : str
        Path to the SQLite database file

    Returns
    -------
    int
        ID of the inserted heatmap data
    """

    # Create engine specific to this function call if db_path is provided
    if db_path != "instance/black_scholes.db":
        local_engine = create_engine(
            f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
        )
        session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=local_engine
        )
        session = session_factory()
    else:
        session = SessionLocal()

    try:
        # Convert numpy array to list for JSON serialization if needed
        data_to_serialize = heatmap_data
        if isinstance(data_to_serialize, np.ndarray):
            data_to_serialize = data_to_serialize.tolist()

        # Serialize the heatmap data to JSON
        heatmap_json_str = json.dumps({"data": data_to_serialize})

        # Create heatmap instance
        heatmap = HeatmapData(
            calculation_id=calculation_id,
            heatmap_type=heatmap_type,
            min_spot=min_spot,
            max_spot=max_spot,
            min_vol=min_vol,
            max_vol=max_vol,
            spot_steps=spot_steps,
            vol_steps=vol_steps,
            heatmap_json=heatmap_json_str,
        )

        # Add to session and commit
        session.add(heatmap)
        session.commit()

        # Get ID of inserted heatmap
        return cast(int, heatmap.id)
    finally:
        session.close()
