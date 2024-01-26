import numpy
# in this file we will decalre the parametrs that will be used in the project

ModoDelsys = True # True if we use the Delsys API Server, False if we use the API Server from the PM.
MusclesNumber = 2
synergysNumber = MusclesNumber
RawData_BufferSize = 1000 

SynergyBase = numpy.identity(MusclesNumber)
synergy_CursorMap = [0,1,2,3]
CursorMovement_Gain = 20



  

