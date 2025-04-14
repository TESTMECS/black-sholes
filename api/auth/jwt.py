"""
JWT authentication for FastAPI.
"""

import jwt
import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(days=1)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Simple user storage - in production use a database
users = {
    # username: {password_hash, role}
}


def create_jwt_token(data: Dict) -> str:
    """
    Create a JWT token.

    Parameters
    ----------
    data : Dict
        Data to encode in the token

    Returns
    -------
    str
        JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + JWT_EXPIRATION_DELTA
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> Dict:
    """
    Decode a JWT token.

    Parameters
    ----------
    token : str
        JWT token to decode

    Returns
    -------
    Dict
        Decoded token data

    Raises
    ------
    HTTPException
        If the token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Get the current user from the JWT token.

    Parameters
    ----------
    token : str
        JWT token

    Returns
    -------
    str
        Username of the current user

    Raises
    ------
    HTTPException
        If the user is not found
    """
    payload = decode_jwt_token(token)
    username = payload.get("sub")
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username
