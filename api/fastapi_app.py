"""
FastAPI application for the Black-Scholes API.
"""

import subprocess
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api.routes import register_routers
from logging import getLogger

logger = getLogger(__name__)


# Global variable to store the Streamlit process
streamlit_process = None
streamlit_port = 8501  # Default Streamlit port
api_description = """
This API provides authenticated access to the Black-Scholes option pricing model calculations and heatmaps stored in the database.
Save your calculations and heatmaps in the streamlit application and then access them with this API.
"""


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Start Streamlit when the FastAPI app starts
    start_streamlit()
    yield
    # Stop Streamlit when the FastAPI app stops
    stop_streamlit()


# Create FastAPI app
app = FastAPI(
    title="Black-Scholes API",
    description=api_description,
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def start_streamlit():
    """Start the Streamlit application as a subprocess"""
    logger.debug("Starting Streamlit application...")
    global streamlit_process
    if streamlit_process is None or streamlit_process.poll() is not None:
        # Start Streamlit on the specified port
        streamlit_process = subprocess.Popen(
            [
                "streamlit",
                "run",
                "streamlit_app.py",
                "--server.port",
                str(streamlit_port),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        time.sleep(2)
        return True
    return False


def stop_streamlit():
    """Stop the Streamlit application if it's running"""
    global streamlit_process
    if streamlit_process and streamlit_process.poll() is None:
        # Try to terminate gracefully first
        streamlit_process.terminate()
        try:
            # Wait for process to terminate
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't terminate
            streamlit_process.kill()
        streamlit_process = None
        return True
    return False


@app.get("/", response_class=HTMLResponse, tags=["streamlit"])
async def index():
    """Redirect to the Streamlit app"""
    # Start Streamlit if it's not already running
    logger.debug("Hit index route")
    start_streamlit()
    # Redirect to the Streamlit app
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Black-Scholes Option Pricing Model</title>
        <meta http-equiv="refresh" content="0; url=http://localhost:{streamlit_port}">
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
            }}
            .loader {{
                border: 16px solid #f3f3f3;
                border-top: 16px solid #3498db;
                border-radius: 50%;
                width: 120px;
                height: 120px;
                animation: spin 2s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <h1>Black-Scholes Option Pricing Model</h1>
        <p>Redirecting to the Streamlit application...</p>
        <div class="loader"></div>
    </body>
    </html>
    """


@app.get("/status", tags=["streamlit"])
async def status():
    """Check if Streamlit is running"""
    if streamlit_process and streamlit_process.poll() is None:
        return {"status": "running", "port": streamlit_port}
    else:
        return {"status": "stopped"}


@app.get("/start", tags=["streamlit"])
async def start():
    """Start the Streamlit application"""
    if start_streamlit():
        return {"status": "started", "port": streamlit_port}
    else:
        return {"status": "already_running", "port": streamlit_port}


@app.get("/stop", tags=["streamlit"])
async def stop():
    """Stop the Streamlit application"""
    if stop_streamlit():
        return {"status": "stopped"}
    else:
        return {"status": "not_running"}


@app.get("/restart", tags=["streamlit"])
async def restart():
    """Restart the Streamlit application"""
    stop_streamlit()
    if start_streamlit():
        return {"status": "restarted", "port": streamlit_port}
    else:
        return {"status": "failed_to_restart"}


@app.get("/api", tags=["api"])
async def api_index():
    """Base API route with information"""
    return {
        "name": "Black-Scholes API",
        "version": "1.0.0",
        "description": "API for Black-Scholes option pricing model",
        "endpoints": {
            "auth": "/api/auth",
            "calculations": "/api/calculations",
            "heatmaps": "/api/calculation/{id}/heatmaps",
        },
    }


# Include routers
register_routers(app)

if __name__ == "__main__":
    try:
        import uvicorn

        uvicorn.run("api.fastapi_app:app", host="localhost", port=5000, reload=True)
    except ImportError:
        print(
            "Error: uvicorn is not installed. Please install it with 'pip install uvicorn'."
        )
