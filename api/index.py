import sys
import os

# Add root folder to sys.path to enable loading app.py relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask application instance
from app import app
