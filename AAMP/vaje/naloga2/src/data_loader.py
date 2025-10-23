import numpy as np

def load_data(filepath):
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