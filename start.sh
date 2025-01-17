#!/bin/bash

# Print current directory and Python path
echo "Current directory: $(pwd)"
echo "Python path: $(which python)"

# Set environment variables
export FLASK_APP=src/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Kill any existing Python processes
echo "Killing any existing Flask processes..."
pkill -f "python src/app.py" || true

# Ensure we're in the correct directory
if [ ! -f "src/app.py" ]; then
    echo "Error: src/app.py not found!"
    echo "Directory contents:"
    ls -la
    exit 1
fi

echo "Starting Flask application..."
# Start the Flask application with output
python src/app.py 2>&1 | tee flask.log 