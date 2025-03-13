import json
import numpy as np
import struct
from pathlib import Path

binary_file = "../prepared/points_xsmall.bin"
tree_file = "../prepared/tree_xsmall.txt"

def load_binary_points(file_path):
    """Load points from binary file."""
    # Pre-allocate numpy array for better memory efficiency
    file_size = Path(file_path).stat().st_size
    point_count = file_size // 12  # Each point is 3 floats (12 bytes)
    points = np.empty((point_count, 3), dtype=np.float32)
    
    with open(file_path, 'rb') as f:
        data = f.read()
        
    # Process all points at once using numpy's frombuffer
    points_flat = np.frombuffer(data, dtype=np.float32)
    points = points_flat.reshape(-1, 3)
    
    return points

def validate_node(node_id, node_data, points, tree_data, indent=0):
    """Validate a single node and its children. Returns (is_valid, violations_dict)."""
    prefix = "  " * indent
    print(f"{prefix}Validating node: {node_id}")
    
    violations_dict = {}
    start = node_data['start']
    stop = node_data['stop']
    
    # If it's a leaf node, nothing to validate
    if 'leaf' in node_data:
        print(f"{prefix}Leaf node with {stop - start} points")
        return True, {}
    
    # Get node properties
    dimension = node_data['dimension']
    delim = node_data['delim']
    dim_idx = 0 if dimension == 'x' else 1  # y dimension
    
    # Get left and right children
    left_id = node_data['left']
    right_id = node_data['right']
    split_idx = node_data['split'] - start
    
    # Get views of the points for this node's left and right children
    # This doesn't create copies, just views into the original array
    node_points = points[start:stop]
    left_points = node_points[:split_idx]
    right_points = node_points[split_idx:]
    
    # Validate left child
    left_mask = left_points[:, dim_idx] > delim
    left_violations = []
    if np.any(left_mask):
        violation_indices = np.where(left_mask)[0]
        for i in violation_indices[:5]:  # Only get first 5 violations
            left_violations.append((i + start, left_points[i, dim_idx], left_points[i]))
    
    left_valid = len(left_violations) == 0
    print(f"{prefix}Left child ({left_id}): {len(left_points)} points")
    print(f"{prefix}All points <= {delim} on {dimension}: {left_valid}")
    
    if not left_valid:
        violations_dict[f"node_{node_id}_left"] = {
            "dimension": dimension,
            "delimiter": delim,
            "violations": [(idx, val, point.tolist()) for idx, val, point in left_violations]
        }
        print(f"{prefix}Violations in left child: {left_violations[:5]} ...")
    
    # Validate right child
    right_mask = right_points[:, dim_idx] < delim
    right_violations = []
    if np.any(right_mask):
        violation_indices = np.where(right_mask)[0]
        for i in violation_indices[:5]:  # Only get first 5 violations
            right_violations.append((i + start + split_idx, right_points[i, dim_idx], right_points[i]))
    
    right_valid = len(right_violations) == 0
    print(f"{prefix}Right child ({right_id}): {len(right_points)} points")
    print(f"{prefix}All points >= {delim} on {dimension}: {right_valid}")
    
    if not right_valid:
        violations_dict[f"node_{node_id}_right"] = {
            "dimension": dimension,
            "delimiter": delim,
            "violations": [(idx, val, point.tolist()) for idx, val, point in right_violations]
        }
        print(f"{prefix}Violations in right child: {right_violations[:5]} ...")
    
    # Clear references to temporary views before recursion
    del node_points, left_points, right_points
    
    # Recursively validate children
    left_result, left_child_violations = validate_node(left_id, tree_data['nodes'][left_id], points, tree_data, indent + 1)
    right_result, right_child_violations = validate_node(right_id, tree_data['nodes'][right_id], points, tree_data, indent + 1)
    
    # Merge all violations
    violations_dict.update(left_child_violations)
    violations_dict.update(right_child_violations)
    
    return (left_valid and right_valid and left_result and right_result), violations_dict

def main():
    # Load tree structure
    tree_path = Path(tree_file)
    points_path = Path(binary_file)
    
    print("Loading tree structure...")
    with open(tree_path) as f:
        tree_data = json.load(f)
    
    print("Loading points from binary file...")
    points = load_binary_points(points_path)
    print(f"Loaded {len(points)} points")
    
    print("\nStarting validation...")
    root_id = tree_data['root']
    is_valid, violations = validate_node(root_id, tree_data['nodes'][root_id], points, tree_data)
    
    print("\nValidation complete!")
    print(f"Tree is {'valid' if is_valid else 'invalid'}")
    
    if not is_valid:
        print("\nDetailed violations:")
        for node_key, node_violations in violations.items():
            print(f"\nNode: {node_key}")
            print(f"Dimension: {node_violations['dimension']}")
            print(f"Delimiter: {node_violations['delimiter']}")
            print("Violations (index, value, point):")
            for idx, val, point in node_violations['violations'][:5]:  # Show first 5 violations
                print(f"  Index {idx}: value {val:.6f} at point {point}")
            if len(node_violations['violations']) > 5:
                print(f"  ... and {len(node_violations['violations']) - 5} more violations")

if __name__ == "__main__":
    main() 