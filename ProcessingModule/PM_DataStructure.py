import General.LocalCircularBufferVector as Buffer
from threading import Semaphore
import ProcessingModule.PM_Parameters as params 
import numpy as np

class PM_DataStructure:
    numCols = 8  # Default value, will be updated in __init__
    def __init__(self) -> None:
        if params.MusclesNumber is not None:
            self.numCols = params.MusclesNumber
        self.circular_stack = Buffer.CircularBufferVector(1,self.numCols)
        self.positionOutput = np.zeros(2)

    def InitializeRawDataBuffer(self):
        if params.MusclesNumber is not None:
            self.numCols = params.MusclesNumber
        self.circular_stack = Buffer.CircularBufferVector(params.RawData_BufferSize, self.numCols)

PM_DataStruct = PM_DataStructure()

SynergiesBuffer = []   
ProcessedDataBuffer = []

def InitializeVisualizationBuffers():
    global SynergiesBuffer
    global ProcessedDataBuffer
    SynergiesBuffer = Buffer.CircularBufferVector(1000,params.synergiesNumber)   
    ProcessedDataBuffer = Buffer.CircularBufferVector(1000,params.MusclesNumber)

stack_lock = Semaphore(1)  # Semaphore for main stack access
PositionOutput_Semaphore =  Semaphore(1) 
SynergyBase_Semaphore = Semaphore(1)
SynergiesBuffer_Semaphore = Semaphore(1)
ProcessedDataBuffer_Semaphore = Semaphore(1)