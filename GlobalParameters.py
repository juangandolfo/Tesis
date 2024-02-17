# In this file we will decalre the parametrs that will be used in the PM
import numpy as np
import csvHandler


ModoDelsys = True # True if we use the Delsys API Server, False if we use the API Server from the PM.
Initialized = False


MusclesNumber = 8
synergysNumber = MusclesNumber
RawData_BufferSize = 1000
sampleRate = 1

SynergyConfigurationFile = 'SynergyConfigurationFromExcel.csv'

synergy_CursorMap = [0,1,0,1]
CursorMovement_Gain = 50

SynergyBase = np.identity(8)

PeakActivation = []
Threshold = []

def Initialize():
    global SynergyBase 
    global synergy_CursorMap
    global PeakActivation 
    global Initialized
    global synergysNumber
    global Threshold

    SynergyBase, synergy_CursorMap, MusclesNumberFromCSV, synergysNumber = csvHandler.Read_csv(SynergyConfigurationFile)
    print(SynergyBase)  
    #SynergyBase = np.identity(MusclesNumber)
    #print(SynergyBase)
    if MusclesNumberFromCSV != MusclesNumber:
        raise Exception("The number of muscles in the configuration file is different from the number of muscles in the PM")    
    PeakActivation = np.ones(MusclesNumber) 
    Threshold = np.ones(MusclesNumber) * 0.1
    
    Initialized = True


                
                
      