from flask import Flask, jsonify
import subprocess
import time
import atexit

app = Flask(__name__)

# Global variable to store the Streamlit process
streamlit_process = None
streamlit_port = 8501  # Default Streamlit port


def start_streamlit():
    """Start the Streamlit application as a subprocess"""
    global streamlit_process
    if streamlit_process is None or streamlit_process.poll() is not None:
        # Start Streamlit on the specified port
        streamlit_process = subprocess.Popen(
            ["streamlit", "run", "app.py", "--server.port", str(streamlit_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Wait a moment for Streamlit to start
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


@app.route("/")
def index():
    """Redirect to the Streamlit app"""
    # Start Streamlit if it's not already running
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


@app.route("/status")
def status():
    """Check if Streamlit is running"""
    if streamlit_process and streamlit_process.poll() is None:
        return jsonify({"status": "running", "port": streamlit_port})
    else:
        return jsonify({"status": "stopped"})


@app.route("/start")
def start():
    """Start the Streamlit application"""
    if start_streamlit():
        return jsonify({"status": "started", "port": streamlit_port})
    else:
        return jsonify({"status": "already_running", "port": streamlit_port})


@app.route("/stop")
def stop():
    """Stop the Streamlit application"""
    if stop_streamlit():
        return jsonify({"status": "stopped"})
    else:
        return jsonify({"status": "not_running"})


@app.route("/restart")
def restart():
    """Restart the Streamlit application"""
    stop_streamlit()
    if start_streamlit():
        return jsonify({"status": "restarted", "port": streamlit_port})
    else:
        return jsonify({"status": "failed_to_restart"})


# Start Streamlit when the Flask app starts
def before_first_request():
    start_streamlit()


# Use with_appcontext for Flask 2.0+
app.before_request_funcs.setdefault(None, []).append(before_first_request)


# Stop Streamlit when the Flask app stops
def cleanup():
    stop_streamlit()

# TODO: Add routes for database functions. 


# Register the cleanup function to be called when the app exits
atexit.register(cleanup)

if __name__ == "__main__":
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
