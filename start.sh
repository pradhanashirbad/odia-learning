#!/bin/bash
export FLASK_APP=src/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Kill any existing Python processes
pkill -f "python src/app.py" || true

# Start the Flask application
python src/app.py 