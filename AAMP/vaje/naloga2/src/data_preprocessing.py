"""
Data preprocessing module for linear regression.
"""
import numpy as np

def sort_data(X, y):
    """
    Sort data points based on X values.
    
    Args:
        X (numpy.ndarray): Feature matrix
        y (numpy.ndarray): Target vector
        
    Returns:
        tuple: (sorted_X, sorted_y)
    """
    # Get sorting indices based on first column of X
    sort_idx = np.argsort(X[:, 0])
    return X[sort_idx], y[sort_idx]

def center_data(X, y):
    """
    Center the data by subtracting means.
    
    Args:
        X (numpy.ndarray): Feature matrix
        y (numpy.ndarray): Target vector
        
    Returns:
        tuple: (centered_X, centered_y, X_mean, y_mean)
    """
    # Calculate means
    X_mean = np.mean(X, axis=0)
    y_mean = np.mean(y)
    
    # Center the data
    X_centered = X - X_mean
    y_centered = y - y_mean
    
    return X_centered, y_centered, X_mean, y_mean

def create_polynomial_features(X, degree):
    """
    Create polynomial features up to specified degree.
    
    Args:
        X (numpy.ndarray): Feature matrix
        degree (int): Maximum polynomial degree
        
    Returns:
        numpy.ndarray: Extended feature matrix with polynomial features
    """
    n_samples = X.shape[0]
    
    # Initialize the result matrix with ones (for b0 term)
    X_poly = np.ones((n_samples, 1))
    
    # Add original features and their powers
    for d in range(1, degree + 1):
        X_poly = np.hstack((X_poly, X ** d))
    
    return X_poly 