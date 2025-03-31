import unittest
import sqlite3
import os
import tempfile
from datetime import datetime

# This module doesn't exist yet - we'll implement it later
# from db_storage import (
#    init_db, store_calculation, get_calculations, get_calculation_by_id
# )


class TestSQLiteStorage(unittest.TestCase):
    """Tests for SQLite storage implementation for Black-Scholes calculations."""

    def setUp(self):
        """Create a temporary database for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Connect to the temporary database
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create tables needed for the test
        self.cursor.execute(
            """
        CREATE TABLE calculations (
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

        self.cursor.execute(
            """
        CREATE TABLE heatmap_data (
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

        self.conn.commit()

    def tearDown(self):
        """Close the database connection and delete the temporary file."""
        self.conn.close()
        os.unlink(self.db_path)

    def test_store_calculation(self):
        """Test storing a Black-Scholes calculation in the database."""
        # Sample calculation data
        calculation = {
            "spot_price": 100.0,
            "strike_price": 100.0,
            "time_to_maturity": 1.0,
            "volatility": 0.2,
            "risk_free_rate": 0.05,
            "call_price": 10.45,
            "put_price": 5.57,
        }

        # Insert the calculation
        self.cursor.execute(
            """
        INSERT INTO calculations 
        (timestamp, spot_price, strike_price, time_to_maturity, volatility, risk_free_rate, call_price, put_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.now().isoformat(),
                calculation["spot_price"],
                calculation["strike_price"],
                calculation["time_to_maturity"],
                calculation["volatility"],
                calculation["risk_free_rate"],
                calculation["call_price"],
                calculation["put_price"],
            ),
        )

        calculation_id = self.cursor.lastrowid
        self.conn.commit()

        # Verify the calculation was stored correctly
        self.cursor.execute(
            "SELECT * FROM calculations WHERE id = ?", (calculation_id,)
        )
        row = self.cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[2], calculation["spot_price"])
        self.assertEqual(row[3], calculation["strike_price"])
        self.assertEqual(row[4], calculation["time_to_maturity"])
        self.assertEqual(row[5], calculation["volatility"])
        self.assertEqual(row[6], calculation["risk_free_rate"])
        self.assertEqual(row[7], calculation["call_price"])
        self.assertEqual(row[8], calculation["put_price"])

    def test_store_heatmap_data(self):
        """Test storing heatmap data in the database."""
        # First insert a calculation
        self.cursor.execute(
            """
        INSERT INTO calculations 
        (timestamp, spot_price, strike_price, time_to_maturity, volatility, risk_free_rate, call_price, put_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (datetime.now().isoformat(), 100.0, 100.0, 1.0, 0.2, 0.05, 10.45, 5.57),
        )

        calculation_id = self.cursor.lastrowid

        # Sample heatmap data
        heatmap_data = {
            "heatmap_type": "call_price",
            "min_spot": 90.0,
            "max_spot": 110.0,
            "min_vol": 0.1,
            "max_vol": 0.3,
            "spot_steps": 5,
            "vol_steps": 4,
            "heatmap_json": '{"data": [[10.1, 15.3, 20.5, 25.7, 30.9], [8.2, 13.4, 18.6, 23.8, 29.0], [6.3, 11.5, 16.7, 21.9, 27.1], [4.4, 9.6, 14.8, 20.0, 25.2]]}',
        }

        # Insert the heatmap data
        self.cursor.execute(
            """
        INSERT INTO heatmap_data
        (calculation_id, heatmap_type, min_spot, max_spot, min_vol, max_vol, spot_steps, vol_steps, heatmap_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                calculation_id,
                heatmap_data["heatmap_type"],
                heatmap_data["min_spot"],
                heatmap_data["max_spot"],
                heatmap_data["min_vol"],
                heatmap_data["max_vol"],
                heatmap_data["spot_steps"],
                heatmap_data["vol_steps"],
                heatmap_data["heatmap_json"],
            ),
        )

        self.conn.commit()

        # Verify the heatmap data was stored correctly
        self.cursor.execute(
            "SELECT * FROM heatmap_data WHERE calculation_id = ?", (calculation_id,)
        )
        row = self.cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[1], calculation_id)
        self.assertEqual(row[2], heatmap_data["heatmap_type"])
        self.assertEqual(row[3], heatmap_data["min_spot"])
        self.assertEqual(row[4], heatmap_data["max_spot"])
        self.assertEqual(row[5], heatmap_data["min_vol"])
        self.assertEqual(row[6], heatmap_data["max_vol"])
        self.assertEqual(row[7], heatmap_data["spot_steps"])
        self.assertEqual(row[8], heatmap_data["vol_steps"])
        self.assertEqual(row[9], heatmap_data["heatmap_json"])

    def test_get_calculations(self):
        """Test retrieving all calculations from the database."""
        # Insert multiple test calculations
        for i in range(3):
            self.cursor.execute(
                """
            INSERT INTO calculations 
            (timestamp, spot_price, strike_price, time_to_maturity, volatility, risk_free_rate, call_price, put_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.now().isoformat(),
                    100.0 + i * 10,
                    100.0,
                    1.0,
                    0.2,
                    0.05,
                    10.45 + i,
                    5.57 + i,
                ),
            )

        self.conn.commit()

        # Retrieve and verify all calculations
        self.cursor.execute("SELECT * FROM calculations ORDER BY id")
        rows = self.cursor.fetchall()

        self.assertEqual(len(rows), 3)
        for i, row in enumerate(rows):
            self.assertEqual(row[2], 100.0 + i * 10)  # spot_price
            self.assertEqual(row[7], 10.45 + i)  # call_price
            self.assertEqual(row[8], 5.57 + i)  # put_price

    def test_get_calculation_with_heatmap(self):
        """Test retrieving a calculation with its associated heatmap data."""
        # Insert a calculation
        self.cursor.execute(
            """
        INSERT INTO calculations 
        (timestamp, spot_price, strike_price, time_to_maturity, volatility, risk_free_rate, call_price, put_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (datetime.now().isoformat(), 100.0, 100.0, 1.0, 0.2, 0.05, 10.45, 5.57),
        )

        calculation_id = self.cursor.lastrowid

        # Insert two heatmaps for this calculation
        heatmap_types = ["call_price", "put_price"]
        for heatmap_type in heatmap_types:
            self.cursor.execute(
                """
            INSERT INTO heatmap_data
            (calculation_id, heatmap_type, min_spot, max_spot, min_vol, max_vol, spot_steps, vol_steps, heatmap_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    calculation_id,
                    heatmap_type,
                    90.0,
                    110.0,
                    0.1,
                    0.3,
                    5,
                    4,
                    f'{{"data": "sample {heatmap_type} data"}}',
                ),
            )

        self.conn.commit()

        # Retrieve the calculation with its heatmaps
        self.cursor.execute(
            """
        SELECT c.*, h.heatmap_type, h.heatmap_json
        FROM calculations c
        LEFT JOIN heatmap_data h ON c.id = h.calculation_id
        WHERE c.id = ?
        """,
            (calculation_id,),
        )

        rows = self.cursor.fetchall()

        # We should have two rows (one for each heatmap)
        self.assertEqual(len(rows), 2)

        # Both rows should have the same calculation data
        self.assertEqual(rows[0][0], calculation_id)
        self.assertEqual(rows[0][0], rows[1][0])  # Same ID
        self.assertEqual(rows[0][2], 100.0)  # spot_price

        # But different heatmap types
        heatmap_types_found = [row[9] for row in rows]
        self.assertIn("call_price", heatmap_types_found)
        self.assertIn("put_price", heatmap_types_found)


if __name__ == "__main__":
    unittest.main()

