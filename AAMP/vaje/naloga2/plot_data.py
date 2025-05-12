import matplotlib.pyplot as plt
import numpy as np

# Function to read data from file
def read_data(filename):
    with open(filename, 'r') as f:
        # Skip header
        next(f)
        data = np.loadtxt(f)
    return data[:, 0], data[:, 1]

# Create figure with 3 subplots
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

# Plot linear function
x1, y1 = read_data('data/Linearna funkcija/Podatki.txt')
ax1.scatter(x1, y1, alpha=0.5)
ax1.set_title('Linearna funkcija')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.grid(True)

# Plot multilinear function
x2, y2 = read_data('data/Multilinearna funkcija/Podatki.txt')
ax2.scatter(x2, y2, alpha=0.5)
ax2.set_title('Multilinearna funkcija')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.grid(True)

# Plot polynomial function
x3, y3 = read_data('data/Polinomska funkcija/Podatki.txt')
ax3.scatter(x3, y3, alpha=0.5)
ax3.set_title('Polinomska funkcija')
ax3.set_xlabel('X')
ax3.set_ylabel('Y')
ax3.grid(True)

# Adjust layout and display
plt.tight_layout()
plt.show() 