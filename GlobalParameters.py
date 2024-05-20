# In this file we will decalre the parametrs that will be used in the PM
import numpy as np
import csvHandler


ModoDelsys = True # True if we use the Delsys API Server, False if we use the API Server from the PM.
Initialized = False


MusclesNumber = 4

RawData_BufferSize = 1000
sampleRate = 1
SynergyConfigurationFile = 'SynergyConfigurationFromExcel.csv'

#synergy_CursorMap = [0,1,0,1]
synergy_CursorMap = []
CursorMovement_Gain = 150
SynergyBase = np.identity(4)
SynergyBaseInverse = np.linalg.pinv(SynergyBase)

projectionMatrix = []

AnglesRecieved = False
RequestAngles = False


PeakActivation = []
Threshold = []

TerminateCalibration = False
CalibrationStage = 0

def Initialize(): 
    global SynergyBase 
    global synergy_CursorMap 
    global PeakActivation 
    global Initialized
    global synergiesNumber
    global Threshold
    global projectionMatrix

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





       
      