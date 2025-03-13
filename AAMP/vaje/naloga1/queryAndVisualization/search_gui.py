from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton)
from PyQt6.QtCore import Qt
import sys

class SearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Point Search")
        self.setFixedSize(400, 200)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # X coordinate input
        x_layout = QHBoxLayout()
        x_label = QLabel("X coordinate:")
        self.x_coord = QLineEdit()
        self.x_coord.setText("0.0")  # Default value
        x_layout.addWidget(x_label)
        x_layout.addWidget(self.x_coord)
        layout.addLayout(x_layout)
        
        # Y coordinate input
        y_layout = QHBoxLayout()
        y_label = QLabel("Y coordinate:")
        self.y_coord = QLineEdit()
        self.y_coord.setText("0.0")  # Default value
        y_layout.addWidget(y_label)
        y_layout.addWidget(self.y_coord)
        layout.addLayout(y_layout)
        
        # Search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add some spacing
        layout.addStretch()
        
        # Center the window
        self.center_window()
        
    def center_window(self):
        """Center the window on the screen."""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
    def search(self):
        """Handle search button click."""
        try:
            x = float(self.x_coord.text())
            y = float(self.y_coord.text())
            print(f"Searching for point: x={x}, y={y}")
            # You can add your search logic here
        except ValueError:
            print("Please enter valid numeric coordinates")

def main():
    app = QApplication(sys.argv)
    window = SearchWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 