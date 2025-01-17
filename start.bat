@echo off
:: Activate virtual environment
call .venv\Scripts\activate

:: Set environment variables
set FLASK_APP=src/app.py
set FLASK_ENV=development
set FLASK_DEBUG=1
set PORT=5001

:: Start the Flask application
python src/app.py 