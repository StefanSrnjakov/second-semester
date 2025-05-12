import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from linear_regression import LinearRegression
from main import load_data

class RegressionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Regression Analysis")
        self.root.geometry("1200x800")
        
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
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.visualization_tab = ttk.Frame(self.notebook)
        self.prediction_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.visualization_tab, text='Visualization')
        self.notebook.add(self.prediction_tab, text='Prediction')
        
        self.setup_visualization_tab()
        self.setup_prediction_tab()
    
    def setup_visualization_tab(self):
        # Create frame for model selection
        model_frame = ttk.LabelFrame(self.visualization_tab, text="Select Model")
        model_frame.pack(fill='x', padx=5, pady=5)
        
        # Model selection dropdown
        self.model_var = tk.StringVar(value='linear')
        model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                    values=['linear', 'polynomial', 'multilinear'])
        model_dropdown.pack(side='left', padx=5, pady=5)
        
        # Plot button
        plot_button = ttk.Button(model_frame, text="Plot", command=self.update_plot)
        plot_button.pack(side='left', padx=5, pady=5)
        
        # Create frame for plot
        self.plot_frame = ttk.Frame(self.visualization_tab)
        self.plot_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Initial plot
        self.update_plot()
    
    def setup_prediction_tab(self):
        # Create frame for model selection
        model_frame = ttk.LabelFrame(self.prediction_tab, text="Select Model")
        model_frame.pack(fill='x', padx=5, pady=5)
        
        # Model selection dropdown
        self.pred_model_var = tk.StringVar(value='linear')
        model_dropdown = ttk.Combobox(model_frame, textvariable=self.pred_model_var, 
                                    values=['linear', 'polynomial', 'multilinear'])
        model_dropdown.pack(side='left', padx=5, pady=5)
        
        # Input frame
        input_frame = ttk.LabelFrame(self.prediction_tab, text="Input Values")
        input_frame.pack(fill='x', padx=5, pady=5)
        
        # Create input fields based on model type
        self.input_entries = []
        self.update_input_fields()
        
        # Bind model selection to update input fields
        model_dropdown.bind('<<ComboboxSelected>>', lambda e: self.update_input_fields())
        
        # Predict button
        predict_button = ttk.Button(self.prediction_tab, text="Predict", command=self.make_prediction)
        predict_button.pack(pady=10)
        
        # Result label
        self.result_label = ttk.Label(self.prediction_tab, text="")
        self.result_label.pack(pady=10)
    
    def update_input_fields(self):
        # Clear existing input fields
        for widget in self.prediction_tab.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.winfo_children():
                for child in widget.winfo_children():
                    child.destroy()
        
        # Create new input fields based on selected model
        model_type = self.pred_model_var.get()
        if model_type == 'multilinear':
            for i in range(4):  # 4 features for multilinear
                ttk.Label(self.prediction_tab.winfo_children()[1], 
                         text=f"X{i+1}:").pack(side='left', padx=5)
                entry = ttk.Entry(self.prediction_tab.winfo_children()[1], width=10)
                entry.pack(side='left', padx=5)
                self.input_entries.append(entry)
        else:
            ttk.Label(self.prediction_tab.winfo_children()[1], 
                     text="X:").pack(side='left', padx=5)
            entry = ttk.Entry(self.prediction_tab.winfo_children()[1], width=10)
            entry.pack(side='left', padx=5)
            self.input_entries.append(entry)
    
    def make_prediction(self):
        try:
            model_type = self.pred_model_var.get()
            if model_type == 'multilinear':
                # Get values from all 4 input fields
                values = [float(entry.get()) for entry in self.input_entries]
                X = np.array([values])
            else:
                # Get value from single input field
                X = np.array([[float(self.input_entries[0].get())]])
            
            # Make prediction
            prediction = self.models[model_type].predict(X)
            self.result_label.config(text=f"Prediction: {prediction[0]:.4f}")
        except ValueError:
            self.result_label.config(text="Please enter valid numbers")
    
    def update_plot(self):
        # Clear previous plot
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        # Create new figure
        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Get selected model type
        model_type = self.model_var.get()
        
        if model_type == 'multilinear':
            # Plot each feature vs target
            n_features = self.multilinear_data[0].shape[1]
            importance = self.models[model_type].get_feature_importance()
            
            for i in range(n_features):
                ax.scatter(self.multilinear_data[0][:, i], self.multilinear_data[1], 
                          alpha=0.5, label=f'X{i+1}')
                
                # Generate points for smooth curve
                x_smooth = np.linspace(self.multilinear_data[0][:, i].min(), 
                                     self.multilinear_data[0][:, i].max(), 100)
                X_smooth = np.zeros((100, n_features))
                X_smooth[:, i] = x_smooth
                
                # Make predictions
                y_pred = self.models[model_type].predict(X_smooth)
                ax.plot(x_smooth, y_pred, label=f'Fit X{i+1}')
            
            ax.set_title('Multilinear Regression')
            ax.legend()
        else:
            # Plot for linear and polynomial
            data = self.linear_data if model_type == 'linear' else self.polynomial_data
            ax.scatter(data[0], data[1], color='blue', alpha=0.5, label='Data points')
            
            # Generate points for smooth curve
            X_smooth = np.linspace(data[0].min(), data[0].max(), 100).reshape(-1, 1)
            y_pred = self.models[model_type].predict(X_smooth)
            
            ax.plot(X_smooth, y_pred, color='red', label='Regression line')
            ax.set_title(f'{model_type.capitalize()} Regression')
            ax.legend()
        
        ax.grid(True)
        
        # Add equation
        equation = self.models[model_type].get_equation()
        ax.text(0.05, 0.95, f'Equation: {equation}', 
                transform=ax.transAxes, 
                bbox=dict(facecolor='white', alpha=0.8))
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

def main():
    root = tk.Tk()
    app = RegressionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 