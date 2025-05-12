"""
Main script to run linear regression analysis on the provided data.
"""
import numpy as np
import matplotlib.pyplot as plt
from linear_regression import LinearRegression

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

def plot_regression(X, y, model, title, regression_type='linear'):
    """
    Plot the data points and regression line/curve.
    
    Args:
        X (np.ndarray): Feature matrix
        y (np.ndarray): Target vector
        model (LinearRegression): Fitted model
        title (str): Plot title
        regression_type (str): Type of regression ('linear', 'polynomial', 'multilinear')
    """
    if regression_type == 'multilinear':
        # For multilinear regression, plot each feature vs target
        n_features = X.shape[1]
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        # Get feature importance
        importance = model.get_feature_importance()
        
        for i in range(n_features):
            ax = axes[i]
            ax.scatter(X[:, i], y, color='blue', alpha=0.5, label='Data points')
            
            # Generate points for smooth curve
            x_smooth = np.linspace(X[:, i].min(), X[:, i].max(), 100)
            X_smooth = np.zeros((100, n_features))
            X_smooth[:, i] = x_smooth
            
            # Make predictions
            y_pred = model.predict(X_smooth)
            
            ax.plot(x_smooth, y_pred, color='red', label='Regression line')
            ax.set_xlabel(f'X{i+1}')
            ax.set_ylabel('Y')
            
            # Add feature importance to title
            if importance:
                imp = importance[f'X{i+1}'] * 100
                ax.set_title(f'Feature Importance: {imp:.1f}%')
            
            ax.legend()
            ax.grid(True)
        
        # Add equation to the figure
        equation = model.get_equation()
        fig.text(0.5, 0.02, f'Equation: {equation}', 
                ha='center', bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    else:
        # For linear and polynomial regression
        plt.figure(figsize=(12, 8))
        plt.scatter(X, y, color='blue', label='Data points', alpha=0.5)
        
        # Generate points for smooth curve
        X_smooth = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        
        # Make predictions for smooth curve
        y_pred = model.predict(X_smooth)
        
        # Plot regression line/curve
        plt.plot(X_smooth, y_pred, color='red', label='Regression line')
        
        # Add equation to plot
        equation = model.get_equation()
        plt.text(0.05, 0.95, f'Equation: {equation}', 
                transform=plt.gca().transAxes, 
                bbox=dict(facecolor='white', alpha=0.8))
        
        plt.title(title)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()
        plt.grid(True)
        plt.show()

def main():
    """Main function to run the regression analysis."""
    # Load data for each type of function
    linear_data = load_data('data/Linearna funkcija/Podatki.txt')
    polynomial_data = load_data('data/Polinomska funkcija/Podatki.txt')
    multilinear_data = load_data('data/Multilinearna funkcija/Podatki.txt')
    
    # Create and fit models
    models = {
        'linear': LinearRegression(),
        'polynomial': LinearRegression(),
        'multilinear': LinearRegression()
    }
    
    # Fit linear regression
    models['linear'].fit(linear_data[0], linear_data[1], regression_type='linear')
    
    # Fit polynomial regression
    models['polynomial'].fit(polynomial_data[0], polynomial_data[1], 
                           regression_type='polynomial', degree=3)
    
    # Fit multilinear regression
    models['multilinear'].fit(multilinear_data[0], multilinear_data[1], 
                            regression_type='multilinear')
    
    # Make predictions and print results
    for name, model in models.items():
        print(f"\n{name.capitalize()} Regression Results:")
        print(f"Equation: {model.get_equation()}")
        
        if name == 'multilinear':
            importance = model.get_feature_importance()
            print("\nFeature Importance:")
            for feature, imp in importance.items():
                print(f"{feature}: {imp*100:.1f}%")
        
        # Example prediction
        if name == 'multilinear':
            test_X = np.array([[1.0, 1.0, 1.0, 1.0]])  # Example test point
        else:
            test_X = np.array([[1.0]])  # Example test point
        prediction = model.predict(test_X)
        print(f"\nPrediction for X={test_X[0]}: {prediction[0]}")
        
        # Plot results
        if name == 'linear':
            plot_regression(linear_data[0], linear_data[1], model, 
                          'Linear Regression Results')
        elif name == 'polynomial':
            plot_regression(polynomial_data[0], polynomial_data[1], model, 
                          'Polynomial Regression Results', 'polynomial')
        elif name == 'multilinear':
            plot_regression(multilinear_data[0], multilinear_data[1], model, 
                          'Multilinear Regression Results', 'multilinear')

if __name__ == "__main__":
    main() 