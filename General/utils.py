import numpy as np

def GenerateProjectionMatrix(angles):
    """Generate projection matrix from angles for cursor movement
    
    Args:
        angles: List or array of angles in degrees
        
    Returns:
        numpy.ndarray: Projection matrix with x and y components
    """
    # Convert angles from degrees to radians
    angles_rad = np.radians(angles)
    # Calculate the x and y components of each vector
    x = np.cos(angles_rad)
    y = np.sin(angles_rad)
    # Construct the projection matrix
    projection_matrix = np.column_stack((x, y))
    return projection_matrix
