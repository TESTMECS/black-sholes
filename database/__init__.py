"""
SQLLite database models functions.
Here we will define the init for the database.
"""

# Import the ORM module to make it available to the package
from database.orm import init_db, DB_PATH

# Import the models to ensure they're registered with SQLAlchemy
from database.models.calculations import Calculation
from database.models.heatmap import HeatmapData

# Export the models and init_db function
__all__ = ["init_db", "DB_PATH", "Calculation", "HeatmapData"]
