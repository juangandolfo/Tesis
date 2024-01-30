import numpy as np
# in this file we will decalre the parametrs that will be used in the project

ModoDelsys = True # True if we use the Delsys API Server, False if we use the API Server from the PM.
MusclesNumber = 2
synergysNumber = MusclesNumber
RawData_BufferSize = 1000 

SynergyBase = np.identity(MusclesNumber)
synergy_CursorMap = [1,0,2,3]
CursorMovement_Gain = 2
PeakActivation = np.ones(MusclesNumber)
