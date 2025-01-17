from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def index():
    return "Odia Learning API"

# Import routes after app creation to avoid circular imports
from src.routes import register_routes
register_routes(app)

if __name__ == '__main__':
    app.run() 