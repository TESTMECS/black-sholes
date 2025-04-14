from flask import Blueprint, jsonify, request
from database.models.calculations import (
    get_calculations,
    get_calculation_by_id,
    store_calculation,
)
from api.routes.auth import token_required

calc_bp = Blueprint("calculations", __name__)


@calc_bp.route("/", methods=["GET"])
@token_required
def list_calculations(_current_user):
    """Get a list of calculations with pagination"""
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)

    # Limit the maximum number of results to prevent abuse
    if limit > 500:
        limit = 500

    calculations = get_calculations(limit=limit, offset=offset)
    return jsonify(
        {
            "data": calculations,
            "meta": {"limit": limit, "offset": offset, "count": len(calculations)},
        }
    )


@calc_bp.route("/<int:calculation_id>", methods=["GET"])
@token_required
def get_calculation(_current_user, calculation_id):
    """Get a specific calculation by ID"""
    try:
        calculation = get_calculation_by_id(calculation_id)
        return jsonify(calculation)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@calc_bp.route("/", methods=["POST"])
@token_required
def create_calculation(_current_user):
    """Create a new calculation"""
    data = request.get_json()

    required_fields = [
        "spot_price",
        "strike_price",
        "time_to_maturity",
        "volatility",
        "risk_free_rate",
        "call_price",
        "put_price",
    ]

    # Validate required fields
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        calculation_id = store_calculation(
            spot_price=data["spot_price"],
            strike_price=data["strike_price"],
            time_to_maturity=data["time_to_maturity"],
            volatility=data["volatility"],
            risk_free_rate=data["risk_free_rate"],
            call_price=data["call_price"],
            put_price=data["put_price"],
        )

        # Return the newly created calculation
        calculation = get_calculation_by_id(calculation_id)
        return jsonify(calculation), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
