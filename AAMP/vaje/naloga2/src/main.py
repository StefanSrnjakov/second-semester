"""
Main script to run the regression analysis application.
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication
from .linear_regression import LinearRegression
from .gui import RegressionGUI
from .data_loader import load_data

def run_analysis():
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
    
    # Print results
    for name, model in models.items():
        print(f"\n{name.capitalize()} Regression Results:")
        print(f"Equation: {model.get_equation()}")
        
        if name == 'multilinear':
            importance = model.get_feature_importance()
            print("\nFeature Importance:")
            for feature, imp in importance.items():
                print(f"{feature}: {imp*100:.1f}%")

def main():
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = RegressionGUI()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()