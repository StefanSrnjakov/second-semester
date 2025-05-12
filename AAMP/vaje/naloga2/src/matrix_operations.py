"""
Matrix operations for linear regression.
"""
import numpy as np

def matrix_multiply(A, B):
    """
    Multiply two matrices.
    
    Args:
        A (numpy.ndarray): First matrix
        B (numpy.ndarray): Second matrix
        
    Returns:
        numpy.ndarray: Result of matrix multiplication
    """
    # Convert to numpy arrays if they aren't already
    A = np.array(A)
    B = np.array(B)
    
    # Handle 1D arrays
    if A.ndim == 1:
        A = A.reshape(-1, 1)
    if B.ndim == 1:
        B = B.reshape(-1, 1)
    
    return np.dot(A, B)

def matrix_transpose(A):
    """
    Transpose a matrix.
    
    Args:
        A (numpy.ndarray): Input matrix
        
    Returns:
        numpy.ndarray: Transposed matrix
    """
    return np.array(A).T

def matrix_inverse(A):
    """
    Calculate the inverse of a matrix using regularization to handle singular matrices.
    
    Args:
        A (numpy.ndarray): Input matrix
        
    Returns:
        numpy.ndarray: Inverse matrix
    """
    # Add small regularization term to diagonal
    n = A.shape[0]
    lambda_reg = 1e-10  # Small regularization parameter
    A_reg = A + lambda_reg * np.eye(n)
    
    try:
        return np.linalg.inv(A_reg)
    except np.linalg.LinAlgError:
        # If still singular, use pseudo-inverse
        return np.linalg.pinv(A_reg)

def solve_linear_system(A, b):
    """
    Solve the linear system Ax = b by finding A^(-1) and multiplying with b.
    
    Args:
        A (numpy.ndarray): Coefficient matrix
        b (numpy.ndarray): Right-hand side vector
        
    Returns:
        numpy.ndarray: Solution vector
    """
    # Step 1: Find the inverse of A
    A_inv = matrix_inverse(A)
    
    # Step 2: Multiply A^(-1) with b to get x
    x = matrix_multiply(A_inv, b)
    
    return x 