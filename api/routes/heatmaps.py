from flask import Blueprint, jsonify, request
from database.models.heatmap import store_heatmap_data
from api.routes.auth import token_required
from database.models.calculations import get_calculation_by_id
import json

heatmap_bp = Blueprint("heatmaps", __name__)


@heatmap_bp.route("/calculation/<int:calculation_id>/heatmaps", methods=["GET"])
@token_required
def get_heatmaps(_current_user, calculation_id):
    """Get all heatmaps for a specific calculation"""
    try:
        calculation = get_calculation_by_id(calculation_id)

        # Extract heatmaps from the calculation response
        heatmaps = calculation.get("heatmaps", [])

        return jsonify({"calculation_id": calculation_id, "heatmaps": heatmaps})
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@heatmap_bp.route("/calculation/<int:calculation_id>/heatmaps", methods=["POST"])
@token_required
def add_heatmap(_current_user, calculation_id):
    """Add a new heatmap to a calculation"""
    data = request.get_json()

    required_fields = [
        "heatmap_type",
        "min_spot",
        "max_spot",
        "min_vol",
        "max_vol",
        "spot_steps",
        "vol_steps",
        "heatmap_data",
    ]

    # Validate required fields
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        # Convert heatmap data if it's a string
        heatmap_data = data["heatmap_data"]
        if isinstance(heatmap_data, str):
            try:
                heatmap_data = json.loads(heatmap_data)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON in heatmap_data"}), 400

        heatmap_id = store_heatmap_data(
            calculation_id=calculation_id,
            heatmap_type=data["heatmap_type"],
            min_spot=data["min_spot"],
            max_spot=data["max_spot"],
            min_vol=data["min_vol"],
            max_vol=data["max_vol"],
            spot_steps=data["spot_steps"],
            vol_steps=data["vol_steps"],
            heatmap_data=heatmap_data,
        )

        # Get the updated calculation with the new heatmap
        calculation = get_calculation_by_id(calculation_id)

        return (
            jsonify(
                {
                    "message": "Heatmap added successfully",
                    "heatmap_id": heatmap_id,
                    "calculation": calculation,
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
