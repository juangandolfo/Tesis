import numpy as np
# in this file we will decalre the parametrs that will be used in the project


ModoDelsys = True # True if we use the Delsys API Server, False if we use the API Server from the PM.
Initialized = False

MusclesNumber = 1
synergysNumber = MusclesNumber
RawData_BufferSize = 1000
sampleRate = 1


synergy_CursorMap = [0,1,0,1]
CursorMovement_Gain = 3

SynergyBase = []
PeakActivation = []

def Initialize():
    global SynergyBase 
    global PeakActivation 
    global Initialized

    SynergyBase = np.identity(MusclesNumber)
    PeakActivation = np.ones(MusclesNumber)
    
    Initialized = True