import tkinter as tk
from tkinter import ttk

class HelloWorldGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hello World")
        self.root.geometry("400x200")
        
        # Set background color for root window
        self.root.configure(bg='white')
        
        # Create a frame with background color
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Create a label with background color
        label = ttk.Label(main_frame, text="Hello, World!", font=('Arial', 24))
        label.pack(pady=20)
        
        # Create a button
        button = ttk.Button(main_frame, text="Click Me!", command=self.on_button_click)
        button.pack(pady=10)
        
        # Create a result label
        self.result_label = ttk.Label(main_frame, text="")
        self.result_label.pack(pady=10)
        
        # Force window to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
    
    def on_button_click(self):
        self.result_label.config(text="Button was clicked!")

def main():
    root = tk.Tk()
    app = HelloWorldGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 