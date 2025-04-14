"""
Authentication routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

from api.models.auth import UserCreate, UserResponse, Token
from api.auth import create_jwt_token, users, JWT_EXPIRATION_DELTA

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user: UserCreate):
    """
    Register a new user.

    Parameters
    ----------
    user : UserCreate
        User data

    Returns
    -------
    UserResponse
        Created user data

    Raises
    ------
    HTTPException
        If the user already exists
    """
    if user.username in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    # Store hashed password
    password_hash = generate_password_hash(user.password)

    # In a real app, save to database
    users[user.username] = {
        "password_hash": password_hash,
        "role": user.role,
    }

    return UserResponse(username=user.username, role=user.role)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login a user.

    Parameters
    ----------
    form_data : OAuth2PasswordRequestForm
        Form data with username and password

    Returns
    -------
    Token
        JWT token

    Raises
    ------
    HTTPException
        If the credentials are invalid
    """
    username = form_data.username
    password = form_data.password

    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = users[username]

    if not check_password_hash(user["password_hash"], password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token
    payload = {
        "sub": username,
        "role": user["role"],
        "iat": datetime.now(timezone.utc),
    }
    token = create_jwt_token(payload)
    expires = (datetime.now(timezone.utc) + JWT_EXPIRATION_DELTA).isoformat()

    return Token(token=token, expires=expires)
