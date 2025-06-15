"""
Frontend application for the Masterblog API.
This module provides a web interface for interacting with the blog API.
"""

import socket
from flask import Flask, render_template
from flask_cors import CORS
import sys
import os

def is_port_in_use(port: int) -> bool:
    """
    Check if a specific port is already in use.

    Args:
        port (int): The port number to check

    Returns:
        bool: True if port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return False
        except socket.error:
            return True

def find_available_port(start_port: int) -> int:
    """
    Find the next available port starting from a specified port number.

    Args:
        start_port (int): The port number to start searching from

    Returns:
        int: Available port number, None if no port is found within range
    """
    port = start_port
    while is_port_in_use(port):
        port += 1
        if port > start_port + 100:  # Limit the search to 100 ports
            return None
    return port

# Initialize Flask application with CORS support
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    """
    Render the main page of the blog application.

    Returns:
        str: Rendered HTML template for the main page
    """
    return render_template("index.html")

def cleanup_and_exit(signal_number=None, frame=None):
    """
    Clean up resources and exit the application gracefully.

    Args:
        signal_number: Signal number received (optional)
        frame: Current stack frame (optional)
    """
    print("\nShutting down the server...")
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

if __name__ == '__main__':
    import signal

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_and_exit)   # Ctrl+C
    signal.signal(signal.SIGTERM, cleanup_and_exit)  # Terminal shutdown

    DEFAULT_PORT = 5004
    port = find_available_port(DEFAULT_PORT)

    if port is None:
        print(f"Error: Could not find an available port starting from {DEFAULT_PORT}")
        sys.exit(1)

    if port != DEFAULT_PORT:
        print(f"Port {DEFAULT_PORT} is in use. Using port {port} instead.")

    print(f"\nStarting server on port {port}")
    print("Press Ctrl+C to stop the server")

    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
