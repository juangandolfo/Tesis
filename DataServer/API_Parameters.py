import numpy as np
import threading
from PySide2.QtCore import *
from PySide2.QtCore import QObject, Signal
import json
import time
import os

#csvFile = '202465_213928.csv'              #tiene 2 musculos
#csvFile = 'Experiment-20240626-220405.csv' #tiene 3 musculos
#csvFile = '202468_195248.csv'               #tiene 4 musculos
# csvFile = 'experimento_prueba.csv'
#csvFile = "C:\Users\pablo\OneDrive\Research\Tesis\RawData.csv"
SimulationFrequency = 2148

KeysLen = 0
ChannelsNumber = 0
SampleRate = 0
SensorStickers = []
Channels_ID = []

StartCalibration = False
TerminateCalibrationFlag = False
CalibrationStageInitialized = False
CalibrationStageFinished = False
CalibrationStage = 0
selectedSensorIndex = 0
SimulationCalibration = False

AnglesReady = 0
AnglesOutput = []
AnglesOutputSemaphore = threading.Semaphore(1)

Thresholds = [0,0]
Peaks = [0,0]
SynergiesModels = []
SynergiesNumber = 2
SynergyBase = []

PlotThresholds = False
PlotPeaks = False
PlotModels = False
PlotAngles = False
PlotUploadedConfig = False

def set_plot_flag(flag_name, value):
    """Debug helper to track when plot flags are set"""
    print(f"[DEBUG] Setting {flag_name} = {value}")
    globals()[flag_name] = value

def debug_plot_state():
    """Debug helper to print current plot state"""
    print(f"[DEBUG] Plot State - Thresholds: {PlotThresholds}, Peaks: {PlotPeaks}, Models: {PlotModels}, Angles: {PlotAngles}, UploadedConfig: {PlotUploadedConfig}")


TimeCalibStage1 = 10
TimeCalibStage2 = 15
TimeCalibStage3 = 30

remaining_time = 5

ExperimentTimestamp = ''

class PlotSignal(QObject):
    signal = Signal()  # Define the signal attribute

PlotCalibrationSignal = PlotSignal()

def TwoDigitString(number):
    if number < 10:
        return "0" + str(number)
    else:
        return str(number)

def CreateExperimentName():
    global ExperimentTimestamp
    print("[DEBUG] Creating experiment name")
    t = time.gmtime()
    UTF = -3
    ExperimentTimestamp = str(t.tm_year) + TwoDigitString(t.tm_mon) + TwoDigitString(t.tm_mday) + "-" + TwoDigitString(t.tm_hour - UTF) + TwoDigitString(t.tm_min) + TwoDigitString(t.tm_sec)
    print(f"[DEBUG] Experiment timestamp: {ExperimentTimestamp}")
    
def UploadCalibrationFromJson():
    print("[DEBUG] Uploading calibration from JSON")
    # Load the configuration from a JSON file
    try:
        with open('Configuration.json') as file:
            print("[DEBUG] Configuration.json opened successfully")
            data = json.load(file)
            
            # Sanity check: Verify all required fields exist
            required_fields = ['MusclesNumber', 'Thresholds', 'Peaks', 'Angles', 'SynergyBase', 'SensorStickers']
            for field in required_fields:
                if field not in data:
                    raise Exception(f"Missing required field '{field}' in configuration file. Please select another file.")
            
            muscles_number = data['MusclesNumber']
            thresholds = data['Thresholds']
            peaks = data['Peaks']
            angles = data['Angles']
            synergy_base = data['SynergyBase']
            sensor_stickers_from_file = data['SensorStickers']
            
            # Sanity check: Verify array lengths match MusclesNumber
            if len(angles) != muscles_number:
                raise Exception(f"Angles array length ({len(angles)}) does not match MusclesNumber ({muscles_number}). Please select another file.")
            
            if len(peaks) != muscles_number:
                raise Exception(f"Peaks array length ({len(peaks)}) does not match MusclesNumber ({muscles_number}). Please select another file.")
            
            if len(thresholds) != muscles_number:
                raise Exception(f"Thresholds array length ({len(thresholds)}) does not match MusclesNumber ({muscles_number}). Please select another file.")
            
            if len(sensor_stickers_from_file) != muscles_number:
                raise Exception(f"SensorStickers array length ({len(sensor_stickers_from_file)}) does not match MusclesNumber ({muscles_number}). Please select another file.")
            
            # Sanity check: Verify SynergyBase is a square matrix of size MusclesNumber x MusclesNumber
            if len(synergy_base) != muscles_number:
                raise Exception(f"SynergyBase array length ({len(synergy_base)}) does not match MusclesNumber ({muscles_number}). Please select another file.")
            
            for i, row in enumerate(synergy_base):
                if len(row) != muscles_number:
                    raise Exception(f"SynergyBase row {i} length ({len(row)}) does not match MusclesNumber ({muscles_number}). SynergyBase must be a square matrix. Please select another file.")
            
            # Check if current number of available sensors matches MusclesNumber
            if ChannelsNumber != muscles_number:
                print(f"[DEBUG] Channel number mismatch: current={ChannelsNumber}, config={muscles_number}")
                raise Exception(f"The number of current available sensors ({ChannelsNumber}) does not match the MusclesNumber in the configuration file ({muscles_number}). Please select another file.")
            
            # Check if current SensorStickers matches file's SensorStickers
            if SensorStickers != sensor_stickers_from_file:
                print(f"[WARNING] Current sensor stickers {SensorStickers} do not match file's sensor stickers {sensor_stickers_from_file}. Loading file anyway but ignoring file's sensor stickers.")
                # Use current SensorStickers instead of file's
                final_sensor_stickers = SensorStickers
            else:
                final_sensor_stickers = sensor_stickers_from_file
                
            print("[DEBUG] All sanity checks passed, configuration loaded successfully")
            return thresholds, peaks, angles, synergy_base, final_sensor_stickers
            
    except FileNotFoundError:
        print("[DEBUG] Configuration.json not found")
        raise Exception("Configuration.json file not found. Please select another file.")
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON decode error: {e}")
        raise Exception(f"Invalid JSON format in configuration file: {e}. Please select another file.")
        
def SaveCalibrationToJson(ChannelsNumber,Thresholds, Peaks, AnglesOutput, SynergyBase, SensorStickers):
    global ExperimentTimestamp
    print("[DEBUG] Saving calibration to JSON")
    data = {
            'MusclesNumber': ChannelsNumber,
            'Thresholds': np.asarray(Thresholds).tolist(),
            'Peaks': np.asarray(Peaks).tolist() ,
            'Angles': np.asarray(AnglesOutput).tolist(),
            'SynergyBase': np.asarray(SynergyBase).tolist(),
            'SensorStickers': SensorStickers
            }
    json_array = json.dumps(data, sort_keys=True, indent=4)
    
    try:
        f = open('Configuration.json', 'w')
        f.write(json_array) 
        f.close()
        print("[DEBUG] Configuration.json saved successfully")

        # Generate a new folder path using the timestamp
        folder_path = 'ExperimentsFiles/Experiment-' + ExperimentTimestamp
        print(f"[DEBUG] Creating experiment folder: {folder_path}")

        # Create directory if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Open the file inside the new folder
        file_path = os.path.join(folder_path, 'Calibration.json')
        print(f"[DEBUG] Saving to experiment file: {file_path}")
        f = open(file_path, 'w')
        f.write(json_array)
        f.close()
        print("[DEBUG] Experiment calibration file saved successfully")
    except Exception as e:
        print(f"[DEBUG] Error saving calibration: {e}")
        raise

def Initialize():
    global SynergyBase
    global SynergiesNumber
    global Thresholds
    global Peaks
    global SensorStickers
    global AnglesOutput
    global SynergiesModels
    global SynergyBase
    
    print(f"[DEBUG] Initializing with {ChannelsNumber} channels")

    SynergyBase = np.identity(ChannelsNumber)
    Thresholds = np.ones(ChannelsNumber) * 0.055
    Peaks = np.ones(ChannelsNumber) * 0.1
    AnglesOutput = [0] * ChannelsNumber
    vafs = [0] * (ChannelsNumber -1)
    SynergiesNumber = ChannelsNumber
    
    SynergiesModels = {
    f'{i+2} Synergies': [np.identity(ChannelsNumber)[k % ChannelsNumber].tolist() for k in range(i+2)]
    for i in range(SynergiesNumber - 1)
    }
    SynergiesModels['vafs'] = (np.asarray(vafs)).tolist()
    print("[DEBUG] Initialization completed")

