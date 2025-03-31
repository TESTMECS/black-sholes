"""
SQLAlchemy ORM model for calculations table.
"""

from sqlalchemy import Column, Integer, Float, String, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json
from typing import List, Dict, Any, cast

from database.orm import Base, SessionLocal


class Calculation(Base):
    """SQLAlchemy model for calculations table."""

    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(
        String, nullable=False, default=lambda: datetime.now().isoformat()
    )
    spot_price = Column(Float, nullable=False)
    strike_price = Column(Float, nullable=False)
    time_to_maturity = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    risk_free_rate = Column(Float, nullable=False)
    call_price = Column(Float, nullable=False)
    put_price = Column(Float, nullable=False)

    # Relationship with HeatmapData
    heatmaps = relationship(
        "HeatmapData", back_populates="calculation", cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "spot_price": self.spot_price,
            "strike_price": self.strike_price,
            "time_to_maturity": self.time_to_maturity,
            "volatility": self.volatility,
            "risk_free_rate": self.risk_free_rate,
            "call_price": self.call_price,
            "put_price": self.put_price,
        }


def store_calculation(
    spot_price: float,
    strike_price: float,
    time_to_maturity: float,
    volatility: float,
    risk_free_rate: float,
    call_price: float,
    put_price: float,
    db_path: str = "instance/black_scholes.db",
) -> int:
    """
    Store a Black-Scholes calculation in the database.

    Parameters
    ----------
    spot_price : float
        Current asset price
    strike_price : float
        Strike price
    time_to_maturity : float
        Time to maturity in years
    volatility : float
        Volatility
    risk_free_rate : float
        Risk-free interest rate
    call_price : float
        Calculated call option price
    put_price : float
        Calculated put option price
    db_path : str
        Path to the SQLite database file

    Returns
    -------
    int
        ID of the inserted calculation
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
        # Create calculation instance
        calculation = Calculation(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_maturity=time_to_maturity,
            volatility=volatility,
            risk_free_rate=risk_free_rate,
            call_price=call_price,
            put_price=put_price,
            timestamp=datetime.now().isoformat(),
        )

        # Add to session and commit
        session.add(calculation)
        session.commit()

        # Get ID of inserted calculation
        return cast(int, calculation.id)
    finally:
        session.close()


def get_calculations(
    limit: int = 100, offset: int = 0, db_path: str = "instance/black_scholes.db"
) -> List[Dict[str, Any]]:
    """
    Get a list of Black-Scholes calculations from the database.

    Parameters
    ----------
    limit : int
        Maximum number of results to return
    offset : int
        Number of results to skip
    db_path : str
        Path to the SQLite database file

    Returns
    -------
    List[Dict[str, Any]]
        List of calculation dictionaries
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
        # Query calculations ordered by id descending
        calculations = (
            session.query(Calculation)
            .order_by(Calculation.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        # Convert to dictionaries
        result = [calc.to_dict() for calc in calculations]

        return result
    finally:
        session.close()


def get_calculation_by_id(
    calculation_id: int, db_path: str = "instance/black_scholes.db"
) -> Dict[str, Any]:
    """
    Get a specific calculation by its ID, including associated heatmap data.

    Parameters
    ----------
    calculation_id : int
        ID of the calculation to retrieve
    db_path : str
        Path to the SQLite database file

    Returns
    -------
    Dict[str, Any]
        Dictionary containing calculation data and associated heatmaps
    """

    from database.models.heatmap import HeatmapData

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
        # Get calculation by ID
        calculation = (
            session.query(Calculation).filter(Calculation.id == calculation_id).first()
        )

        if not calculation:
            return {}

        # Convert calculation to dict
        result = calculation.to_dict()

        # Get associated heatmaps
        heatmaps = (
            session.query(HeatmapData)
            .filter(HeatmapData.calculation_id == calculation_id)
            .all()
        )

        # Process heatmap data
        heatmaps_dict = {}
        for heatmap in heatmaps:
            heatmap_type = heatmap.heatmap_type

            # Parse JSON data
            heatmap_data = json.loads(str(heatmap.heatmap_json))["data"]

            # Add metadata and parsed data
            heatmaps_dict[heatmap_type] = {
                "min_spot": heatmap.min_spot,
                "max_spot": heatmap.max_spot,
                "min_vol": heatmap.min_vol,
                "max_vol": heatmap.max_vol,
                "spot_steps": heatmap.spot_steps,
                "vol_steps": heatmap.vol_steps,
                "data": heatmap_data,
            }

        result["heatmaps"] = heatmaps_dict

        return result
    finally:
        session.close()
