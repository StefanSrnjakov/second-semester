import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QComboBox, QPushButton, QLabel, 
                            QLineEdit, QGroupBox, QTabWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QSpinBox)
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from .linear_regression import LinearRegression
from .data_loader import load_data

class RegressionGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Regression Analysis")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create models dictionary
        self.models = {
            'linear': LinearRegression(),
            'polynomial': LinearRegression(),
            'multilinear': LinearRegression()
        }
        
        # Load data
        self.linear_data = load_data('data/Linearna funkcija/Podatki.txt')
        self.polynomial_data = load_data('data/Polinomska funkcija/Podatki.txt')
        self.multilinear_data = load_data('data/Multilinearna funkcija/Podatki.txt')
        
        # Fit models
        self.models['linear'].fit(self.linear_data[0], self.linear_data[1], regression_type='linear')
        self.models['polynomial'].fit(self.polynomial_data[0], self.polynomial_data[1], 
                                    regression_type='polynomial', degree=3)
        self.models['multilinear'].fit(self.multilinear_data[0], self.multilinear_data[1], 
                                     regression_type='multilinear')
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.visualization_tab = QWidget()
        self.prediction_tab = QWidget()
        
        self.tabs.addTab(self.visualization_tab, "Visualization")
        self.tabs.addTab(self.prediction_tab, "Prediction")
        
        self.setup_visualization_tab()
        self.setup_prediction_tab()
    
    def setup_visualization_tab(self):
        layout = QVBoxLayout(self.visualization_tab)
        
        # Model selection group
        model_group = QGroupBox("Select Model")
        model_layout = QHBoxLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(['linear', 'polynomial', 'multilinear'])
        model_layout.addWidget(self.model_combo)
        
        plot_button = QPushButton("Plot")
        plot_button.clicked.connect(self.update_plot)
        model_layout.addWidget(plot_button)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Plot area
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Initial plot
        self.update_plot()
    
    def setup_prediction_tab(self):
        layout = QVBoxLayout(self.prediction_tab)
        
        # Model selection group
        model_group = QGroupBox("Model Selection")
        model_layout = QHBoxLayout()
        
        self.pred_model_combo = QComboBox()
        self.pred_model_combo.addItems(['linear', 'polynomial', 'multilinear'])
        self.pred_model_combo.currentTextChanged.connect(self.update_prediction_fields)
        model_layout.addWidget(QLabel("Select Model:"))
        model_layout.addWidget(self.pred_model_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Number of predictions control
        num_pred_group = QGroupBox("Number of Predictions")
        num_pred_layout = QHBoxLayout()
        self.num_predictions = QSpinBox()
        self.num_predictions.setMinimum(1)
        self.num_predictions.setMaximum(10)
        self.num_predictions.setValue(1)
        self.num_predictions.valueChanged.connect(self.update_prediction_fields)
        num_pred_layout.addWidget(QLabel("Number of predictions:"))
        num_pred_layout.addWidget(self.num_predictions)
        num_pred_layout.addStretch()
        num_pred_group.setLayout(num_pred_layout)
        layout.addWidget(num_pred_group)
        
        # Input fields container
        self.input_container = QWidget()
        self.input_layout = QVBoxLayout(self.input_container)
        layout.addWidget(self.input_container)
        
        # Predict button
        predict_button = QPushButton("Calculate Predictions")
        predict_button.clicked.connect(self.make_multiple_predictions)
        layout.addWidget(predict_button)
        
        # Initialize prediction fields
        self.prediction_groups = []
        self.update_prediction_fields()
    
    def update_prediction_fields(self):
        # Clear existing prediction groups
        for group, _, _ in self.prediction_groups:
            self.input_layout.removeWidget(group)
            group.deleteLater()
        self.prediction_groups.clear()
        
        # Create new prediction groups
        num_predictions = self.num_predictions.value()
        model_type = self.pred_model_combo.currentText()
        
        for i in range(num_predictions):
            group = QGroupBox(f"Prediction {i+1}")
            group_layout = QVBoxLayout()
            
            # Input fields
            input_layout = QHBoxLayout()
            entries = []
            
            if model_type == 'multilinear':
                for j in range(4):
                    field_layout = QVBoxLayout()
                    field_layout.addWidget(QLabel(f"X{j+1}:"))
                    entry = QLineEdit()
                    entry.setFixedWidth(100)
                    field_layout.addWidget(entry)
                    input_layout.addLayout(field_layout)
                    entries.append(entry)
            else:
                field_layout = QVBoxLayout()
                field_layout.addWidget(QLabel("X:"))
                entry = QLineEdit()
                entry.setFixedWidth(100)
                field_layout.addWidget(entry)
                input_layout.addLayout(field_layout)
                entries.append(entry)
            
            input_layout.addStretch()
            group_layout.addLayout(input_layout)
            
            # Result label
            result_label = QLabel("")
            result_label.setAlignment(Qt.AlignCenter)
            result_label.setStyleSheet("font-weight: bold;")
            group_layout.addWidget(result_label)
            
            group.setLayout(group_layout)
            self.input_layout.addWidget(group)
            self.prediction_groups.append((group, entries, result_label))
        
        # Add stretch at the bottom
        self.input_layout.addStretch()
    
    def make_multiple_predictions(self):
        try:
            model_type = self.pred_model_combo.currentText()
            
            for group, entries, result_label in self.prediction_groups:
                if model_type == 'multilinear':
                    values = []
                    for entry in entries:
                        if entry.text():
                            values.append(float(entry.text()))
                        else:
                            values.append(0.0)
                    X = np.array([values])
                else:
                    if entries[0].text():
                        X = np.array([[float(entries[0].text())]])
                    else:
                        X = np.array([[0.0]])
                
                prediction = self.models[model_type].predict(X)
                result_label.setText(f"Prediction: {prediction[0]:.4f}")
                result_label.setStyleSheet("color: green; font-weight: bold;")
                
        except ValueError:
            # If any input is invalid, show error
            for _, _, result_label in self.prediction_groups:
                result_label.setText("Invalid input")
                result_label.setStyleSheet("color: red; font-weight: bold;")
    
    def update_plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        model_type = self.model_combo.currentText()
        
        if model_type == 'multilinear':
            n_features = self.multilinear_data[0].shape[1]
            importance = self.models[model_type].get_feature_importance()
            
            for i in range(n_features):
                ax.scatter(self.multilinear_data[0][:, i], self.multilinear_data[1], 
                          alpha=0.5, label=f'X{i+1}')
                
                x_smooth = np.linspace(self.multilinear_data[0][:, i].min(), 
                                     self.multilinear_data[0][:, i].max(), 100)
                X_smooth = np.zeros((100, n_features))
                X_smooth[:, i] = x_smooth
                
                y_pred = self.models[model_type].predict(X_smooth)
                ax.plot(x_smooth, y_pred, label=f'Fit X{i+1}')
            
            ax.set_title('Multilinear Regression')
            ax.legend()
        else:
            data = self.linear_data if model_type == 'linear' else self.polynomial_data
            ax.scatter(data[0], data[1], color='blue', alpha=0.5, label='Data points')
            
            X_smooth = np.linspace(data[0].min(), data[0].max(), 100).reshape(-1, 1)
            y_pred = self.models[model_type].predict(X_smooth)
            
            ax.plot(X_smooth, y_pred, color='red', label='Regression line')
            ax.set_title(f'{model_type.capitalize()} Regression')
            ax.legend()
            
            # Format y-axis to show full numbers
            ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.0f'))
            
            # Add padding to the top of the plot only for polynomial regression
            if model_type == 'polynomial':
                y_min, y_max = ax.get_ylim()
                ax.set_ylim(y_min, y_max + 500000)
        
        ax.grid(True)
        
        # Add equation
        equation = self.models[model_type].get_equation()
        ax.text(0.05, 0.95, f'Equation: {equation}', 
                transform=ax.transAxes, 
                bbox=dict(facecolor='white', alpha=0.8))
        
        self.canvas.draw()

def main():
    app = QApplication(sys.argv)
    window = RegressionGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 