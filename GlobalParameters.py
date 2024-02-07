# In this file we will decalre the parametrs that will be used in the PM
import numpy as np
import csvHandler


ModoDelsys = True # True if we use the Delsys API Server, False if we use the API Server from the PM.
Initialized = False
getConfigurationFromCsv = True

MusclesNumber = 8
synergysNumber = MusclesNumber
RawData_BufferSize = 1000
sampleRate = 1

SynergyConfigurationFile = 'SynergyConfiguration.csv'

synergy_CursorMap = [0,1,0,1]
CursorMovement_Gain = 3

SynergyBase = np.identity(8)

PeakActivation = []
Noise = []

def Initialize():
    global SynergyBase 
    global PeakActivation 
    global Initialized

    if getConfigurationFromCsv:
        try:
            csvHandler.Read_csv(SynergyConfigurationFile, synergysNumber, MusclesNumber)
        except Exception as e:
            print(e)
    PeakActivation = np.ones(MusclesNumber) 
    
    Initialized = True




