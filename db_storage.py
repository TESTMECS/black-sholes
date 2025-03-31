import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Union
import numpy as np


def init_db(db_path: str = "black_scholes.db") -> None:
    """
    Initialize the SQLite database with the necessary tables.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create calculations table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        spot_price REAL NOT NULL,
        strike_price REAL NOT NULL,
        time_to_maturity REAL NOT NULL,
        volatility REAL NOT NULL,
        risk_free_rate REAL NOT NULL,
        call_price REAL NOT NULL,
        put_price REAL NOT NULL
    )
    """
    )

    # Create heatmap_data table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS heatmap_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        calculation_id INTEGER NOT NULL,
        heatmap_type TEXT NOT NULL,
        min_spot REAL NOT NULL,
        max_spot REAL NOT NULL,
        min_vol REAL NOT NULL,
        max_vol REAL NOT NULL,
        spot_steps INTEGER NOT NULL,
        vol_steps INTEGER NOT NULL,
        heatmap_json TEXT NOT NULL,
        FOREIGN KEY (calculation_id) REFERENCES calculations (id)
    )
    """
    )

    conn.commit()
    conn.close()


def store_calculation(
    spot_price: float,
    strike_price: float,
    time_to_maturity: float,
    volatility: float,
    risk_free_rate: float,
    call_price: float,
    put_price: float,
    db_path: str = "black_scholes.db",
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
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert the calculation
    cursor.execute(
        """
    INSERT INTO calculations 
    (timestamp, spot_price, strike_price, time_to_maturity, volatility, risk_free_rate, call_price, put_price)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            datetime.now().isoformat(),
            spot_price,
            strike_price,
            time_to_maturity,
            volatility,
            risk_free_rate,
            call_price,
            put_price,
        ),
    )

    calculation_id = cursor.lastrowid
    assert calculation_id is not None
    conn.commit()
    conn.close()

    return calculation_id


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
    db_path: str = "black_scholes.db",
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
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Convert numpy array to list for JSON serialization if needed
    if isinstance(heatmap_data, np.ndarray):
        heatmap_data = heatmap_data.tolist()

    # Serialize the heatmap data to JSON
    heatmap_json = json.dumps({"data": heatmap_data})

    # Insert the heatmap data
    cursor.execute(
        """
    INSERT INTO heatmap_data
    (calculation_id, heatmap_type, min_spot, max_spot, min_vol, max_vol, spot_steps, vol_steps, heatmap_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            calculation_id,
            heatmap_type,
            min_spot,
            max_spot,
            min_vol,
            max_vol,
            spot_steps,
            vol_steps,
            heatmap_json,
        ),
    )

    heatmap_id = cursor.lastrowid
    assert heatmap_id is not None
    conn.commit()
    conn.close()

    return heatmap_id


def get_calculations(
    limit: int = 100, offset: int = 0, db_path: str = "black_scholes.db"
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
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return results as dictionaries
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT * FROM calculations
    ORDER BY id DESC
    LIMIT ? OFFSET ?
    """,
        (limit, offset),
    )

    # Convert row objects to dictionaries
    calculations = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return calculations


def get_calculation_by_id(
    calculation_id: int, db_path: str = "black_scholes.db"
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
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get the calculation
    cursor.execute("SELECT * FROM calculations WHERE id = ?", (calculation_id,))
    calculation = dict(cursor.fetchone())

    if not calculation:
        conn.close()
        return {}

    # Get associated heatmap data
    cursor.execute(
        "SELECT * FROM heatmap_data WHERE calculation_id = ?", (calculation_id,)
    )
    heatmaps_rows = cursor.fetchall()

    # Process heatmap data
    heatmaps = {}
    for row in heatmaps_rows:
        row_dict = dict(row)
        heatmap_type = row_dict["heatmap_type"]

        # Parse JSON data
        heatmap_data = json.loads(row_dict["heatmap_json"])["data"]

        # Add all metadata and the parsed data
        heatmaps[heatmap_type] = {
            "min_spot": row_dict["min_spot"],
            "max_spot": row_dict["max_spot"],
            "min_vol": row_dict["min_vol"],
            "max_vol": row_dict["max_vol"],
            "spot_steps": row_dict["spot_steps"],
            "vol_steps": row_dict["vol_steps"],
            "data": heatmap_data,
        }

    calculation["heatmaps"] = heatmaps
    conn.close()

    return calculation
