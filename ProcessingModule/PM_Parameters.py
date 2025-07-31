# In this file we will decalre the parametrs that will be used in the PM
import numpy as np
#import csvHandler
from scipy.signal import butter
import pymsgbox as msgbox
from ProcessingModule.FileHandler import LogHandler, FileHandler
import os
import json
import csv

ModoDelsys = True # True if we use the Delsys API Server, False if we use the API Server from the PM.
SubSamplingRate = 100
saveCSV = True

Initialized = False

MusclesNumber = None
SensorStickers = []

RawData_BufferSize = 500
sampleRate = 1
Subsampling_NumberOfSamples = sampleRate/SubSamplingRate 
SynergyConfigurationFile = 'SynergyConfigurationFromExcel.csv'
synergy_CursorMap = []
CursorMovement_Gain = 500
SynergyBase = None 
SynergyBaseInverse = None
modelsList = []
output = []
recommendedModelNumber = 2
synergiesNumber = None
vafs = []
# Convert angles from degrees to radians
angles_rad = None
# Calculate the x and y components of each vector
x = None
y = None
# Construct the projection matrix
projectionMatrix = None

RequestCalibrationTime = False
AnglesRecieved = False
RequestAngles = False
PlotThresholds = False
PlotPeaks = False
PlotSynergiesDetected = False
DetectingSynergies = False
UploadFromJson = False
JsonReceived = False
UploadSimulationConfig = False
Processing = False
InitializeCalibration = False
InitializeCalibrationRequest = False
PeakActivation = []
Threshold = []

PingResponse = 0
PingRequested = False
PingTimeFromDataServer = 0.0

TerminateCalibration = False
CalibrationStage = 0
TimeCalibStage3 = 30
Muscle2Calibrate_index = 0

logHandler = 0
attempt = 0
fileHandler = 0

ExperimentTimestamp = ''
sampleCounter = 0

#LPF
LPF_cutoff = 40
LPF_order = 4
coefficient1 = 0
coefficient2 = 0

def Initialize():
    global SynergyBase
    global synergy_CursorMap
    global PeakActivation
    global Initialized
    global synergiesNumber
    global Threshold
    global projectionMatrix
    global coefficient1
    global coefficient2
    global logHandler
    global attempt
    global RawDataFileName
    global fileHandler

    '''SynergyBase, synergy_CursorMap, MusclesNumberFromCSV, synergysNumber = csvHandler.Read_csv(SynergyConfigurationFile)
    print(SynergyBase)
    #SynergyBase = np.identity(MusclesNumber)
    #print(SynergyBase)
    if MusclesNumberFromCSV != MusclesNumber:
        raise Exception("The number of muscles in the configuration file is different from the number of muscles in the PM")    '''
    # PeakActivation = np.ones(MusclesNumber)*0.1
    # Threshold = np.ones(MusclesNumber) * 0.055
    # synergiesNumber = MusclesNumber
    # synergy_CursorMap = np.zeros(MusclesNumber) #pensar en cambiar esto por algo equiespaciado (360*i/musclesunmber)

    # for synergy in range(synergiesNumber):
    #     synergy_CursorMap[synergy] = 360*synergy/synergiesNumber
    # projectionMatrix = GenerateProjectionMatrix(synergy_CursorMap)

    nyquist = 0.5 * sampleRate
    normal_cutoff = LPF_cutoff / nyquist
    coefficient2, coefficient1 = butter(LPF_order, normal_cutoff, btype='low', analog=False)

    modelsList = {}

    for i in range(2, synergiesNumber + 1):
        n_components = i

        # Create h_norm with repeated identity pattern
        h_norm = np.array([np.identity(MusclesNumber)[k % MusclesNumber] for k in range(n_components)])

        H_inv = np.linalg.pinv(h_norm)
        r_squared = np.zeros(1)
        vaf = np.zeros(1)

        modelsList[i - 2] = (n_components, h_norm, H_inv, r_squared, vaf)  # use integer key
   
    # Generate a new folder path using the timestamp
    folder_path = 'ExperimentsFiles/Experiment-' + ExperimentTimestamp
    os.makedirs(folder_path, exist_ok=True)  # Create the folder, no error if it already exists
    if saveCSV:
        RawDataFileName = 'ExperimentsFiles\Experiment-' + ExperimentTimestamp + "\RawData.csv"
        file = open(RawDataFileName, 'w', newline='')
        writer = csv.writer(file)
        columns = ['Sample'] + [f'Muscle {i+1}' for i in range(MusclesNumber)]
        writer.writerow(columns)

    fileHandler = FileHandler(folder_path)
    logHandler = LogHandler(folder_path)
    attempt = Attempt()   

    Initialized = True

def GenerateProjectionMatrix(angles):
    # Convert angles from degrees to radians
    angles_rad = np.radians(synergy_CursorMap)
    # Calculate the x and y components of each vector
    x = np.cos(angles_rad)
    y = np.sin(angles_rad)
    # Construct the projection matrix
    projectionMatrix = np.column_stack((x, y))
    return projectionMatrix

class Attempt():
    def __init__(self):
        self.Id = 0
        self.Start = sampleCounter
        self.Stop = sampleCounter
        self.Result = ""
        self.Target = 0
        self.File = "ExperimentsFiles/Experiment-" + ExperimentTimestamp + "/Events.json" 
        self.initializeExperimentFile()

    def convertToJson(self):
        attemptDictionary = {
            "Id": self.Id,
            "Start": self.Start,
            "Stop": self.Stop,
            "Result": self.Result,
            "Target": self.Target,
        }
        return attemptDictionary
    
    def initializeExperimentFile(self):
        filename = self.File
        # Check if file exists to avoid overwriting
        if not os.path.exists(filename):
            experiment_data = []
            with open(filename, 'w') as file:
                json.dump(experiment_data, file, indent=4)
    
    def saveAttempt(self):
        # Check if file exists to avoid overwriting
        with open(self.File) as file:
            data = json.load(file)
            data.append(self.convertToJson())
            with open(self.File, 'w') as file:
                json.dump(data, file, indent=4) 
        self.incrementId() 

    def setStart(self):
        self.Start = sampleCounter 

    def setTarget(self, target):
        self.Target = target

    def setStop(self):
        self.Stop = sampleCounter

    def setResult(self, result):
        self.Result = result    
    
    def incrementId(self):
        self.Id += 1

