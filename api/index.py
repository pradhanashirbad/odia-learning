import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import app

# Vercel requires the app to be named 'app'
app.debug = False

if __name__ == '__main__':
    app.run() 