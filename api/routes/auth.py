from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from functools import wraps

auth_bp = Blueprint("auth", __name__)

# In production, this should be stored securely in environment variables
# or a configuration service
JWT_SECRET = os.environ.get("JWT_SECRET", "development_secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = datetime.timedelta(days=1)

# Simple user storage - in production use a database
users = {
    # username: {password_hash, role}
}


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            # Decode the token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user = payload["sub"]
            if current_user not in users:
                return jsonify({"message": "Invalid user"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Missing required fields"}), 400

    username = data["username"]

    if username in users:
        return jsonify({"message": "User already exists"}), 409

    # Store hashed password
    password_hash = generate_password_hash(data["password"])

    # In a real app, save to database
    users[username] = {
        "password_hash": password_hash,
        "role": data.get("role", "user"),  # Default to user role
    }

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Missing required fields"}), 400

    username = data["username"]

    if username not in users:
        return jsonify({"message": "Invalid credentials"}), 401

    user = users[username]

    if check_password_hash(user["password_hash"], data["password"]):
        # Generate JWT token
        payload = {
            "sub": username,
            "role": user["role"],
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA,
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return (
            jsonify(
                {
                    "token": token,
                    "expires": (
                        datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA
                    ).isoformat(),
                }
            ),
            200,
        )

    return jsonify({"message": "Invalid credentials"}), 401
