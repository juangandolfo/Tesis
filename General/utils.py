import json
import numpy as np

def check_calibration_json(filename, expected_stickers):
    """
    Checks the calibration JSON file for consistency based on the provided sensor_info.
    sensor_info: list of stickers or scalar number of sensors
    Returns True if all checks pass, False otherwise.
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[CHECK] Error loading JSON: {e}")
        return False

    # Always require a sticker list as input
    sensor_count = len(expected_stickers)
    # SensorStickers key must exist
    if 'SensorStickers' not in data:
        print("[CHECK] SensorStickers key missing in JSON.")
        return False
    json_stickers = data['SensorStickers']
    if len(json_stickers) != sensor_count:
        print(f"[CHECK] SensorStickers length mismatch: expected {sensor_count}, got {len(json_stickers)}.")
        return False
    missing = [s for s in expected_stickers if s not in json_stickers]
    if missing:
        print(f"[CHECK] Missing stickers in JSON: {missing}")
        return False

    # Check Thresholds and Peaks
    for key in ['Thresholds', 'Peaks']:
        if key in data:
            arr = data[key]
            if not isinstance(arr, list) or len(arr) != sensor_count:
                print(f"[CHECK] {key} length mismatch: expected {sensor_count}, got {len(arr)}.")
                return False
        else:
            print(f"[CHECK] {key} key not found in JSON (optional). Continuing.")

    # Check SynergyBase and Angles logic (cleaner)
    synergy = data.get('SynergyBase', None)
    angles = data.get('Angles', None)
    if synergy is not None:
        if not isinstance(synergy, list) or len(synergy) == 0:
            print("[CHECK] SynergyBase must be a non-empty list.")
            return False
        n_angles = len(synergy)
        # If Angles exists, check it
        if angles is not None:
            if not isinstance(angles, list) or len(angles) != n_angles or not all(isinstance(a, (int, float, np.integer, np.floating)) for a in angles):
                print(f"[CHECK] Angles must be a list of {n_angles} numbers.")
                return False
        else:
            angles = list(np.linspace(0, 360, n_angles, endpoint=False))
            print(f"[CHECK] Angles key missing, created equally spaced angles: {angles}")
        # Validate synergy structure
        for i, s in enumerate(synergy):
            if not isinstance(s, list) or len(s) != sensor_count or not all(isinstance(x, (int, float, np.integer, np.floating)) for x in s):
                print(f"[CHECK] SynergyBase[{i}] must be a list of {sensor_count} numbers.")
                return False
    else:
        # SynergyBase does not exist
        if angles is not None:
            print("[CHECK] Angles key exists but SynergyBase is missing. Ignoring Angles.")
        # No further checks needed
    # All checks passed
    return True
