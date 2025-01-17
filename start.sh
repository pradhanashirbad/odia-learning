#!/bin/bash

# Activate virtual environment (if using one)
source .venv/Scripts/activate  # For Windows
# source .venv/bin/activate   # For Linux/Mac (uncomment this line and comment the above if on Linux/Mac)

# Set environment variables (if needed)
export FLASK_APP=src/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export PORT=5001

# Start the Flask application
python src/app.py 