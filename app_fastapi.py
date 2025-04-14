"""
Entry point for the FastAPI application.
"""

from api.fastapi_app import app

if __name__ == "__main__":
    try:
        import uvicorn

        uvicorn.run(app, host="localhost", port=5000, reload=True)
    except ImportError:
        print(
            "Error: uvicorn is not installed. Please install it with 'pip install uvicorn'."
        )
