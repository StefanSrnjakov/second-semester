import numpy as np
import struct
from pathlib import Path

# File path
BINARY_FILE = "../prepared/points.bin"

def get_random_point():
    """Get a random point from binary file."""
    # Get file size and calculate number of points
    file_size = Path(BINARY_FILE).stat().st_size
    point_size = 12  # 3 floats * 4 bytes
    total_points = file_size // point_size
    
    # Generate random point index
    random_index = np.random.randint(0, total_points)
    
    # Read the random point
    with open(BINARY_FILE, 'rb') as f:
        # Seek to the random point position
        f.seek(random_index * point_size)
        # Read 12 bytes (3 float32 values)
        point_data = f.read(point_size)
        # Unpack the bytes into 3 float values
        x, y, z = struct.unpack('fff', point_data)
        
    return x, y, z

if __name__ == "__main__":
    x, y, z = get_random_point()
    print(f"Random point: x={x:.6f}, y={y:.6f}, z={z:.6f}") 