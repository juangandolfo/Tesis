# In this file we will decalre the parametrs that will be used in the PM
import numpy as np
import csvHandler


ModoDelsys = True # True if we use the Delsys API Server, False if we use the API Server from the PM.
Initialized = False


MusclesNumber = 4
synergysNumber = MusclesNumber
RawData_BufferSize = 1000
sampleRate = 1

SynergyConfigurationFile = 'SynergyConfigurationFromExcel.csv'

#synergy_CursorMap = [0,1,0,1]
synergy_CursorMap = [45,115,270]
CursorMovement_Gain = 50
SynergyBase = np.identity(4)
SynergyBaseInverse = np.linalg.pinv(SynergyBase)

# Convert angles from degrees to radians
angles_rad = np.radians(synergy_CursorMap)
# Calculate the x and y components of each vector
x = np.cos(angles_rad)
y = np.sin(angles_rad)
# Construct the projection matrix
projectionMatrix = np.column_stack((x, y))        


PeakActivation = []
Threshold = []

TerminateCalibration = False
CalibrationStage = 0

def Initialize(): 
    global SynergyBase 
    global synergy_CursorMap 
    global PeakActivation 
    global Initialized
    global synergysNumber
    global Threshold

    '''SynergyBase, synergy_CursorMap, MusclesNumberFromCSV, synergysNumber = csvHandler.Read_csv(SynergyConfigurationFile)
    print(SynergyBase)  
    #SynergyBase = np.identity(MusclesNumber)
    #print(SynergyBase)
    if MusclesNumberFromCSV != MusclesNumber:
        raise Exception("The number of muscles in the configuration file is different from the number of muscles in the PM")    '''
    PeakActivation = np.ones(MusclesNumber)*0.1 
    Threshold = np.ones(MusclesNumber) * 0.055
    
    Initialized = True


       
      