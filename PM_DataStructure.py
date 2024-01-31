import LocalCircularBufferVector as Buffer
from threading import Semaphore
import GlobalParameters
import numpy as np

class PM_DataStructure:
    def __init__(self) -> None:
        self.circular_stack = Buffer.CircularBufferVector(1, GlobalParameters.MusclesNumber)
        self.positionOutput = np.zeros(2)

    def InitializeRawDataBuffer(self):
        self.circular_stack = Buffer.CircularBufferVector(GlobalParameters.RawData_BufferSize, GlobalParameters.MusclesNumber)

PM_DataStruct = PM_DataStructure()

stack_lock = Semaphore(1)  # Semaphore for stack access
PositionOutput_Semaphore =  Semaphore(1) 
SynergyBase_Semaphore = Semaphore(1)