"""
Script to run the linear regression analysis.
"""
import sys
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.append(src_dir)

# Import main function from src.main
from src.main import main

if __name__ == "__main__":
    main() 