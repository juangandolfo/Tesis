import PM_DataStructure as PM_DS
import numpy as np
from threading import Thread
import GlobalParameters
import time

import csv
import numpy as np

# Function to save data to a CSV file
def save_to_csv(filename, aux_vector, M1, M2):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Thresholds', 'M1', 'M2'])
        for i in range(len(aux_vector)):
            writer.writerow([aux_vector[i], M1[i], M2[i]])

class DataProcessing:

    def __init__(self):
        self.LastOutputWeight = 0.5
          
    def Rectify(self, data):
        return np.abs(data)
    
    def Normalize(self, data, peaks, size,threshold):
        for i in range(size):
            '''
            if data[i] > peaks[i]:
                peaks[i] = data[i]'''
            data[i] = max(0, data[i] - threshold[i])
        return data/(peaks-threshold)
    
    def DummyLowPassFilter(self, data, LastOutput):
        return np.array(LastOutput)*self.LastOutputWeight + np.array(data)*(1-self.LastOutputWeight)

    def Set_LastOutputWeight(self, Weight):
        self.LastOutputWeight = Weight

    def MapActivation(self,matriz, data):
        return np.matmul(data.T, matriz).T

    def UpdatePosition(self,synergyActivation,synergy_CursorMap):
        
        longitud_deseada = 8
        ceros_faltantes = longitud_deseada - len(synergyActivation)
        synergyActivation = np.pad(synergyActivation, ((0,0),(0, ceros_faltantes)), mode='constant')[0]
        left,right,up,down = synergy_CursorMap
        return np.array([synergyActivation[right]-synergyActivation[left],synergyActivation[up]-synergyActivation[down]])

DataProcessing = DataProcessing()
LastRawData = [0 for i in range(GlobalParameters.MusclesNumber)]

def Processing():
    print("PM: Processing live")
    
    LastNormalizedData = [0 for i in range(GlobalParameters.MusclesNumber)]
        
    while True:
        
        PM_DS.stack_lock.acquire()  
        RawData = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(1)
        PM_DS.stack_lock.release()
        if RawData != []:
            RectifiedData = DataProcessing.Rectify(RawData)
            NormalizedData = DataProcessing.Normalize(RectifiedData, GlobalParameters.PeakActivation, GlobalParameters.MusclesNumber, GlobalParameters.Threshold)
            ProcessedData = DataProcessing.DummyLowPassFilter(NormalizedData, LastNormalizedData).reshape(-1,1)
            LastNormalizedData = NormalizedData
            
            PM_DS.SynergyBase_Semaphore.acquire()
            SynergyActivations = np.array(DataProcessing.MapActivation(GlobalParameters.SynergyBaseInverse,ProcessedData).T)
            PM_DS.SynergyBase_Semaphore.release()
           

            NewMovement = DataProcessing.UpdatePosition(SynergyActivations, GlobalParameters.synergy_CursorMap)
            
            PM_DS.PositionOutput_Semaphore.acquire()
            PM_DS.PM_DataStruct.positionOutput = PM_DS.PM_DataStruct.positionOutput + GlobalParameters.CursorMovement_Gain*NewMovement/GlobalParameters.sampleRate
            PM_DS.PositionOutput_Semaphore.release()


def CalibrationProcessing():
    
    while(GlobalParameters.Initialized == False):
       pass

    LastData = [0 for i in range(GlobalParameters.MusclesNumber)]

    while not GlobalParameters.TerminateCalibration:
        #print("PM: Calibration Processing live")
                

            if GlobalParameters.CalibrationStage == 1:
                print("Detecting Thresholds...")
                thresholds = np.zeros(GlobalParameters.MusclesNumber)
                PM_DS.stack_lock.acquire()
                PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
                PM_DS.stack_lock.release()
                M1=[]
                M2=[]
                Peaks = [[] for _ in range(GlobalParameters.MusclesNumber)]
                while(GlobalParameters.CalibrationStage == 1):
                    PM_DS.stack_lock.acquire()  
                    DataBatch = np.array(PM_DS.PM_DataStruct.circular_stack.get_vectors(1))
                    PM_DS.stack_lock.release()
                    if DataBatch != []:
                        
                        RectifiedMuscleData = DataProcessing.Rectify(DataBatch)
                        for row in range(len(DataBatch)):
                            DataBatch[row]= DataProcessing.DummyLowPassFilter(RectifiedMuscleData[row], LastData)
                            LastData = RectifiedMuscleData[row]

                            DataMuscle=DataBatch[row]
                            M1.append(DataMuscle[0])
                            M2.append(DataMuscle[1]) 

                        for muscle in range(GlobalParameters.MusclesNumber): 
                            Peaks[muscle].append(np.max(DataBatch[:,muscle]))

                for muscle in range(GlobalParameters.MusclesNumber):
                    thresholds[muscle] = np.median(np.array(Peaks[muscle]))

                print("Thresholds:", thresholds)
                GlobalParameters.Threshold = thresholds

            elif GlobalParameters.CalibrationStage == 2:
                print("Detecting Peaks...")
                PM_DS.stack_lock.acquire()
                PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
                PM_DS.stack_lock.release()
                
                while(GlobalParameters.CalibrationStage == 2):
                    PM_DS.stack_lock.acquire()  
                    RawData = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(1)
                    PM_DS.stack_lock.release()
                    if RawData != []:
                        RectifiedData = DataProcessing.Rectify(RawData)
                        ProcessedData = DataProcessing.DummyLowPassFilter(RectifiedData, LastData).reshape(-1,1)
                        LastData = RectifiedData
                    
                        for i in range(GlobalParameters.MusclesNumber):
                            if ProcessedData[i] > GlobalParameters.PeakActivation[i]:
                                GlobalParameters.PeakActivation[i] = ProcessedData[i]
                print("Peaks:", GlobalParameters.PeakActivation)
                
            elif GlobalParameters.CalibrationStage == 3:
                PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
                while(GlobalParameters.CalibrationStage == 3): 
                    print("Bucle stage 3")
       
    print("PM: Calibration terminated")          
    # Plot the vectors
    