import numpy as np

def sort_data(X, y):
    # Get sorting indices based on first column of X
    sort_idx = np.argsort(X[:, 0])
    return X[sort_idx], y[sort_idx]

def center_data(X, y):
    # Calculate means
    X_mean = np.mean(X, axis=0)
    y_mean = np.mean(y)
    
    # Center the data
    X_centered = X - X_mean
    y_centered = y - y_mean
    
    return X_centered, y_centered, X_mean, y_mean

def create_polynomial_features(X, degree):
    n_samples = X.shape[0]
    
    # Initialize the result matrix with ones (for b0 term)
    X_poly = np.ones((n_samples, 1))
    
    # Add original features and their powers
    for d in range(1, degree + 1):
        X_poly = np.hstack((X_poly, X ** d))
    
    return X_poly 