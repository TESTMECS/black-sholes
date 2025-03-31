"""
Test file for SQLAlchemy ORM models.
"""

import tempfile
import numpy as np

from database.models.calculations import store_calculation, get_calculation_by_id
from database.models.heatmap import store_heatmap_data
from database.orm import init_db


def test_orm_models():
    """Test the ORM models for calculations and heatmap data."""
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_path = tmp.name

        # Create the database tables
        init_db(db_path)

        # Test storing a calculation
        calculation_id = store_calculation(
            spot_price=100.0,
            strike_price=105.0,
            time_to_maturity=1.0,
            volatility=0.2,
            risk_free_rate=0.05,
            call_price=8.02,
            put_price=7.49,
            db_path=db_path,
        )

        # Verify calculation was stored and can be retrieved
        calculation = get_calculation_by_id(calculation_id, db_path)
        assert calculation
        assert calculation["spot_price"] == 100.0
        assert calculation["strike_price"] == 105.0

        # Test storing heatmap data
        heatmap_data = np.zeros((5, 5))
        for i in range(5):
            for j in range(5):
                heatmap_data[i, j] = i * 5 + j

        _heatmap_id = store_heatmap_data(
            calculation_id=calculation_id,
            heatmap_type="call_price",
            min_spot=90.0,
            max_spot=110.0,
            min_vol=0.1,
            max_vol=0.3,
            spot_steps=5,
            vol_steps=5,
            heatmap_data=heatmap_data,
            db_path=db_path,
        )

        # Verify that the heatmap data is associated with the calculation
        calculation = get_calculation_by_id(calculation_id, db_path)
        assert calculation
        assert "heatmaps" in calculation
        assert "call_price" in calculation["heatmaps"]
        assert calculation["heatmaps"]["call_price"]["min_spot"] == 90.0
        assert calculation["heatmaps"]["call_price"]["max_spot"] == 110.0

