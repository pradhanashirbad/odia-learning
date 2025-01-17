from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Ensure src directory is in path
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# Import routes after app creation to avoid circular imports
from src.routes import register_routes
register_routes(app)

if __name__ == '__main__':
    app.run() 