from PM_DataStructure import *
import numpy as np
from threading import Thread


class DataProcessing:

    def __init__(self):
        self.LastOutputWeight = 0.5
          
    def Rectify(self, data):
        return np.abs(data)
    
    def DummyLowPassFilter(self, data, LastOutput):
        return np.array(LastOutput)*self.LastOutputWeight + np.array(data)*(1-self.LastOutputWeight)
    
    def Set_LastOutputWeight(self, Weight):
        self.LastOutputWeight = Weight

DataProcessing = DataProcessing()

def Processing():
    stack_lock.acquire()  # Acquire lock before accessing the stack
    LastRawData = circular_stack.get_oldest_vector("identificador nuevo")
    RawData = circular_stack.get_vectors("identificador nuevo")
    if RawData != []:
        ProcessedData = DataProcessing.DummyLowPassFilter(DataProcessing.Rectify(RawData), LastRawData)
        circular_stack.add_vector(ProcessedData)
    stack_lock.release() 
#Hay que programar el puntero en el buffer y agregar delay al cursor.


DataProcessing = DataProcessing()
Processing = Thread(target=Processing)
Processing.start()