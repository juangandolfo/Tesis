# In this file we will decalre the parametrs that will be used in the PM
import numpy as np
#import csvHandler
from scipy.signal import butter
import pymsgbox as msgbox

ModoDelsys = True # True if we use the Delsys API Server, False if we use the API Server from the PM.
SubSamplingRate = 100
saveCSV = False

Initialized = False

MusclesNumber = 8
SensorStickers = []

RawData_BufferSize = 500
sampleRate = 1
Subsampling_NumberOfSamples = sampleRate/SubSamplingRate 
SynergyConfigurationFile = 'SynergyConfigurationFromExcel.csv'
if MusclesNumber == 4:
    synergy_CursorMap = [30,210,120,300]
else:
    synergy_CursorMap = [30,120]
CursorMovement_Gain = 500
SynergyBase = np.identity(MusclesNumber)
SynergyBaseInverse = np.linalg.pinv(SynergyBase)
modelsList = []
output = []
recommendedModelNumber = 2
vafs = []
# Convert angles from degrees to radians
angles_rad = np.radians(synergy_CursorMap)
# Calculate the x and y components of each vector
x = np.cos(angles_rad)
y = np.sin(angles_rad)
# Construct the projection matrix
projectionMatrix = np.column_stack((x, y))

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
PeakActivation = []
Threshold = []

PingResponse = 0
PingRequested = False
PingTimeFromDataServer = 0.0

TerminateCalibration = False
CalibrationStage = 0
TimeCalibStage3 = 10


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

    '''SynergyBase, synergy_CursorMap, MusclesNumberFromCSV, synergysNumber = csvHandler.Read_csv(SynergyConfigurationFile)
    print(SynergyBase)
    #SynergyBase = np.identity(MusclesNumber)
    #print(SynergyBase)
    if MusclesNumberFromCSV != MusclesNumber:
        raise Exception("The number of muscles in the configuration file is different from the number of muscles in the PM")    '''
    PeakActivation = np.ones(MusclesNumber)*0.1
    Threshold = np.ones(MusclesNumber) * 0.055
    synergiesNumber = MusclesNumber
    synergy_CursorMap = np.zeros(MusclesNumber) #pensar en cambiar esto por algo equiespaciado (360*i/musclesunmber)

    for synergy in range(synergiesNumber):
        synergy_CursorMap[synergy] = 360*synergy/synergiesNumber
    projectionMatrix = GenerateProjectionMatrix(synergy_CursorMap)

    nyquist = 0.5 * sampleRate
    normal_cutoff = LPF_cutoff / nyquist
    coefficient2, coefficient1 = butter(LPF_order, normal_cutoff, btype='low', analog=False)

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

