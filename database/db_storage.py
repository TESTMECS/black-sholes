"""
Database storage adapter to expose ORM functions to app.py.
This file provides a compatibility layer between the app and our SQLAlchemy ORM.
TODO: Adapt for the API
"""

# Re-export functions from our ORM models
from database.orm import init_db, DB_PATH
from database.models.calculations import (
    store_calculation,
    get_calculations,
    get_calculation_by_id,
)
from database.models.heatmap import store_heatmap_data

# Export all functions
__all__ = [
    "init_db",
    "DB_PATH",
    "store_calculation",
    "get_calculations",
    "get_calculation_by_id",
    "store_heatmap_data",
]
