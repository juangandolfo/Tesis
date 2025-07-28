import json
import numpy as np
import os

def create_default_configuration(num_muscles):
    """
    Create a default configuration JSON file with the specified number of muscles.
    
    Args:
        num_muscles (int): Number of muscles/sensors
        
    Returns:
        dict: Default configuration dictionary
    """
    # Generate evenly spaced angles from 0 to 360 (exclusive)
    angles = [i * (360 / num_muscles) for i in range(num_muscles)]
    
    # Create identity matrix for synergy base (canonical base)
    synergy_base = np.identity(num_muscles).tolist()
    
    # Generate consecutive sensor stickers
    sensor_stickers = [str(i + 1) for i in range(num_muscles)]
    
    # Default values
    thresholds = [0.1] * num_muscles
    peaks = [0.5] * num_muscles
    
    config = {
        "Angles": angles,
        "MusclesNumber": num_muscles,
        "Peaks": peaks,
        "SensorStickers": sensor_stickers,
        "SynergyBase": synergy_base,
        "Thresholds": thresholds
    }
    
    return config

def save_default_configuration(num_muscles, experiment_folder, filename="Default_Calibration.json"):
    """
    Save a default configuration to the specified experiment folder.
    
    Args:
        num_muscles (int): Number of muscles/sensors
        experiment_folder (str): Path to the experiment folder
        filename (str): Name of the configuration file
        
    Returns:
        str: Path to the saved file
    """
    config = create_default_configuration(num_muscles)
    
    # Ensure experiment folder exists
    os.makedirs(experiment_folder, exist_ok=True)
    
    # Create filename with muscle count and save directly in experiment folder
    filename = f"Default_{num_muscles}muscle_Calibration.json"
    file_path = os.path.join(experiment_folder, filename)
    
    # Save to file
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    return file_path
