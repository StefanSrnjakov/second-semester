import numpy as np
from pathlib import Path

# File paths
csv_file = "../prepared/sorted_points_xsmall_mistaken.csv"
binary_file = "../prepared/points_xsmall_mistaken.bin"

def convert_csv_to_binary():
    print(f"Converting {csv_file} to binary format...")
    
    # Load points from CSV
    points = np.loadtxt(csv_file, delimiter=',', dtype=np.float32)
    
    # Ensure we have a 2D array with 3 columns (x,y,z)
    if len(points.shape) == 1:
        points = points.reshape(-1, 3)
    
    # Write to binary file
    points.tofile(binary_file)
    
    print(f"Converted {len(points)} points to binary format")
    print(f"Output saved to {binary_file}")

if __name__ == "__main__":
    convert_csv_to_binary() 