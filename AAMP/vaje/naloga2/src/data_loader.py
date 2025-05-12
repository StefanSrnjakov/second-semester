"""
Data loading functionality for regression analysis.
"""
import numpy as np

def load_data(filepath):
    """
    Load data from file.
    
    Args:
        filepath (str): Path to the data file
        
    Returns:
        tuple: (X, y) feature matrix and target vector
    """
    # Skip the header row and load the data
    data = np.loadtxt(filepath, skiprows=1)
    
    # For multilinear data, all columns except the last one are features
    if 'Multilinearna' in filepath:
        X = data[:, :-1]  # All columns except the last one
        y = data[:, -1]   # Last column is the target
    else:
        # For linear and polynomial, only first column is feature
        X = data[:, 0].reshape(-1, 1)
        y = data[:, 1]
    
    return X, y 