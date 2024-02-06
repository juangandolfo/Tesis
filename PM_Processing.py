import PM_DataStructure as PM_DS
import numpy as np
from threading import Thread
import GlobalParameters
import time


class DataProcessing:

    def __init__(self):
        self.LastOutputWeight = 0.5
          
    def Rectify(self, data):
        return np.abs(data)
    
    def Normalize(self, data, peaks, size):
        for i in range(size):
            if data[i] > peaks[i]:
                peaks[i] = data[i]
        return data/peaks
    
    def DummyLowPassFilter(self, data, LastOutput):
        return np.array(LastOutput)*self.LastOutputWeight + np.array(data)*(1-self.LastOutputWeight)
    
    def Set_LastOutputWeight(self, Weight):
        self.LastOutputWeight = Weight

    def MapActivation(self,data,matriz):
        return np.matmul(matriz,data)

    def UpdatePosition(self,synergyActivation,synergy_CursorMap):
        longitud_deseada = 8
        ceros_faltantes = longitud_deseada - len(synergyActivation)
        synergyActivation = np.pad(synergyActivation, (0, ceros_faltantes), mode='constant')
        left,right,up,down = synergy_CursorMap
        return np.array([synergyActivation[right]-synergyActivation[left],synergyActivation[up]-synergyActivation[down]])

DataProcessing = DataProcessing()
LastRawData = [0 for i in range(GlobalParameters.MusclesNumber)]

def Processing():
    #print("PM: Processing live")
    while(GlobalParameters.Initialized == False):
       pass

    LastNormalizedData = [0 for i in range(GlobalParameters.MusclesNumber)]
    #print(GlobalParameters.SynergyBase)
    
    while True:
        
        PM_DS.stack_lock.acquire()  
        RawData = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(1)
        PM_DS.stack_lock.release()
        if RawData != []:
            RectifiedData = DataProcessing.Rectify(RawData)
            NormalizedData = DataProcessing.Normalize(RectifiedData, GlobalParameters.PeakActivation, GlobalParameters.MusclesNumber)
            ProcessedData = DataProcessing.DummyLowPassFilter(NormalizedData, LastNormalizedData)
            LastNormalizedData = NormalizedData
            #print(ProcessedData)
            PM_DS.SynergyBase_Semaphore.acquire()
            SynergyActivations = DataProcessing.MapActivation(ProcessedData,GlobalParameters.SynergyBase)
            PM_DS.SynergyBase_Semaphore.release()

            NewMovement = DataProcessing.UpdatePosition(SynergyActivations, GlobalParameters.synergy_CursorMap)
            
            PM_DS.PositionOutput_Semaphore.acquire()
            PM_DS.PM_DataStruct.positionOutput = PM_DS.PM_DataStruct.positionOutput + GlobalParameters.CursorMovement_Gain*NewMovement/GlobalParameters.sampleRate
            PM_DS.PositionOutput_Semaphore.release()


