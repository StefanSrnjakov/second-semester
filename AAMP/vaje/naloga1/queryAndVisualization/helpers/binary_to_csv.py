import numpy as np
from pathlib import Path

# File paths
binary_file = "../prepared/points_xsmall.bin"
csv_file = "../prepared/points_xsmall.csv"

def convert_binary_to_csv():
    print(f"Converting {binary_file} to CSV format...")
    
    # Get file size and calculate number of points
    file_size = Path(binary_file).stat().st_size
    point_count = file_size // (3 * 4)  # 3 floats * 4 bytes each
    
    # Read binary data
    points = np.fromfile(binary_file, dtype=np.float32)
    points = points.reshape(-1, 3)
    
    # Save to CSV
    np.savetxt(csv_file, points, delimiter=',', fmt='%.6f')
    
    print(f"Converted {len(points)} points to CSV format")
    print(f"Output saved to {csv_file}")

if __name__ == "__main__":
    convert_binary_to_csv() 