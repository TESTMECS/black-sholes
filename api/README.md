# Black-Scholes API Documentation

This API provides authenticated access to the Black-Scholes option pricing model calculations and heatmaps stored in the database.

## API Implementation

The API is implemented using FastAPI, a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

Key features:
- JWT-based authentication
- Pydantic models for request/response validation
- Automatic OpenAPI documentation
- SQLAlchemy ORM for database access

## Authentication

The API uses JWT (JSON Web Token) authentication. To use the API, you need to:

1. Register a user
2. Login to get a JWT token
3. Include the token in subsequent requests

### User Registration

```
POST /api/auth/register
```

Request body:

```json
{
  "username": "your_username",
  "password": "your_password",
  "role": "user" // Optional, defaults to "user"
}
```

### User Login

```
POST /api/auth/login
```

Request body:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:

```json
{
  "token": "your_jwt_token",
  "expires": "expiration_datetime"
}
```

## Using the API

For all API endpoints except registration and login, you must include the JWT token in the Authorization header:

```
Authorization: Bearer your_jwt_token
```

## Calculation Endpoints

### List Calculations

```
GET /api/calculations?limit=100&offset=0
```

Parameters:

- `limit` (optional): Maximum number of results to return (default: 100, max: 500)
- `offset` (optional): Number of results to skip (default: 0)

### Get Calculation by ID

```
GET /api/calculations/{calculation_id}
```

### Create Calculation

```
POST /api/calculations
```

Request body:

```json
{
  "spot_price": 100.0,
  "strike_price": 100.0,
  "time_to_maturity": 1.0,
  "volatility": 0.2,
  "risk_free_rate": 0.05,
  "call_price": 10.45,
  "put_price": 5.57
}
```

## Heatmap Endpoints

### Get Heatmaps for a Calculation

```
GET /api/calculation/{calculation_id}/heatmaps
```

### Add Heatmap to a Calculation

```
POST /api/calculation/{calculation_id}/heatmaps
```

Request body:

```json
{
  "heatmap_type": "call_price",
  "min_spot": 80.0,
  "max_spot": 120.0,
  "min_vol": 0.1,
  "max_vol": 0.4,
  "spot_steps": 20,
  "vol_steps": 20,
  "heatmap_data": [[...], [...], ...]
}
```

## API Information

```
GET /api
```

Returns information about the API and available endpoints.

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

These documentation pages allow you to:
- View all available endpoints
- See request/response models
- Try out the API directly from the browser

## Running the API

To run the API:

```bash
python app_fastapi.py
```

This will start the FastAPI server on port 5000. You can access the API at:

- API: http://localhost:5000/api
- Documentation: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc
