import numpy as np
import threading
from PySide2.QtCore import *
from PySide2.QtCore import QObject, Signal
import json
import time
import os

DelsysMode = False
#csvFile = '202465_213928.csv'              #tiene 2 musculos
#csvFile = 'Experiment-20240626-220405.csv' #tiene 3 musculos
#csvFile = '202468_195248.csv'               #tiene 4 musculos
# csvFile = 'experimento_prueba.csv'
#csvFile = 'ExperimentsFiles\Experiment-20241202-261323\RawData.csv'
csvFile = 'ExperimentsFiles\Experiment-20250521-031035\RawData.csv'
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
    
def UploadCalibrationFromJson(filename = 'Configuration.json'):
    # Load the configuration from a JSON file
    with open(filename) as file:
        data = json.load(file)
        if ChannelsNumber != data['MusclesNumber']:
            raise Exception("The number of channels in the configuration file is different from the current configuration")
        else:
            # Agregar chequeo de que existen las keys previo a enviarlas, si no existe devolver null (notorio que no existe), 
            # validar que el json sea consistente por ejemplo que sensor stickers tenga el mismo numero de elementos que los thresholds y peaks
            # Get all keys from data
            ValidKeys = ['Thresholds', 'Peaks', 'Angles', 'SynergyBase', 'SensorStickers']
            dictionary = {}
            keys = data.keys()
            for key in ValidKeys:
                if key not in keys:
                    dictionary[key] = None
                    # Output to VSCode's debug console 
                    print(f"                                                Key '{key}' not found in JSON data.", flush=True)
                else:
                    dictionary[key] = data[key]
            
            Thresholds = dictionary['Thresholds']
            Peaks = dictionary['Peaks']
            AnglesOutput = dictionary['Angles']
            SynergiesModels= dictionary['SynergyBase']
            SensorStickers = dictionary['SensorStickers']

            # Agregar alarm (msgbox) si no es consistente
            # Devolver todo en un dictionary 
    return Thresholds, Peaks, AnglesOutput, SynergiesModels, SensorStickers

def UploadProjectionFromJson():
    # Load the projection from a JSON file
    with open('Configuration.json') as file:
        data = json.load(file)
        if ChannelsNumber != data['MusclesNumber']:
            raise Exception("The number of channels in the projection file is different from the current configuration")
        else:
            SynergyBase = data['SynergyBase']
            AnglesOutput = data['Angles']
    return SynergyBase, AnglesOutput
        
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

    SynergyBase = np.identity(ChannelsNumber).tolist()

    # Thresholds = np.ones(ChannelsNumber) * 0.055
    Thresholds = [0.055] * ChannelsNumber
    # Peaks = np.ones(ChannelsNumber) * 0.1
    Peaks = [0.1] * ChannelsNumber
    AnglesOutput = [0] * ChannelsNumber
    vafs = [0] * (ChannelsNumber -1)
    SynergiesNumber = ChannelsNumber
    
    SynergiesModels = {
    f'{i+2} Synergies': [np.identity(ChannelsNumber)[k % ChannelsNumber].tolist() for k in range(i+2)]
    for i in range(SynergiesNumber - 1)
    }
    SynergiesModels['vafs'] = (np.asarray(vafs)).tolist()
    print("[DEBUG] Initialization completed")

