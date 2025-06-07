"""
Main linear regression implementation.
"""
import numpy as np
from .matrix_operations import matrix_multiply, matrix_transpose, solve_linear_system
from .data_preprocessing import sort_data, center_data, create_polynomial_features

class LinearRegression:
    def __init__(self):
        """Initialize the LinearRegression model."""
        self.coefficients = None
        self.b0 = None
        self.X_mean = None
        self.y_mean = None
        self.regression_type = None
        self.degree = None
        self.feature_names = None
    
    def fit(self, X, y, regression_type='linear', degree=1):
        self.regression_type = regression_type
        self.degree = degree
        
        # Ensure X is 2D and y is 1D
        X = np.array(X)
        y = np.array(y)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        # Store feature names for multilinear regression
        if regression_type == 'multilinear':
            self.feature_names = [f'X{i+1}' for i in range(X.shape[1])]
        
        # Sort data
        X, y = sort_data(X, y)
        
        # Create polynomial features if needed
        if regression_type == 'polynomial':
            X = create_polynomial_features(X, degree)
        
        # Center data
        X_centered, y_centered, self.X_mean, self.y_mean = center_data(X, y)
        
        # Calculate coefficients using least squares
        X_T = matrix_transpose(X_centered)
        X_T_X = matrix_multiply(X_T, X_centered)
        X_T_y = matrix_multiply(X_T, y_centered.reshape(-1, 1))
        
        # Solve the system using robust method
        self.coefficients = solve_linear_system(X_T_X, X_T_y)
        
        # Calculate b0
        b0_values = []
        for i in range(len(X)):
            # Calculate b0 for each sample
            b0 = y[i] - np.sum(self.coefficients.flatten() * X[i])
            b0_values.append(b0)
        
        # Take the mean of all b0 values
        self.b0 = np.mean(b0_values)
    
    def predict(self, X):
        if self.coefficients is None:
            raise ValueError("Model not fitted yet!")
        
        # Ensure X is 2D
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        # Create polynomial features if needed
        if self.regression_type == 'polynomial':
            X = create_polynomial_features(X, self.degree)
        
        # Make prediction
        y_pred = np.dot(X, self.coefficients) + self.b0
        
        return y_pred.flatten()
    
    def get_equation(self):
        if self.coefficients is None:
            return "Model not fitted yet!"
        
        equation = f"y = {self.b0:.4f}"
        
        if self.regression_type == 'linear':
            equation += f" + {self.coefficients[0][0]:.4f}x"
        elif self.regression_type == 'polynomial':
            for i, coef in enumerate(self.coefficients):
                if i == 0:
                    equation += f" + {coef[0]:.4f}x"
                else:
                    equation += f" + {coef[0]:.4f}x^{i+1}"
        elif self.regression_type == 'multilinear':
            for i, coef in enumerate(self.coefficients):
                equation += f" + {coef[0]:.4f}{self.feature_names[i]}"
        
        return equation
    
    def get_feature_importance(self):
        if self.regression_type != 'multilinear' or self.coefficients is None:
            return None
        
        # Calculate importance as absolute coefficient values
        importance = np.abs(self.coefficients.flatten())
        
        # Normalize importance scores
        importance = importance / np.sum(importance)
        
        return dict(zip(self.feature_names, importance)) 