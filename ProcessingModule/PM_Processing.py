import ProcessingModule.PM_DataStructure as PM_DS
import General.LocalCircularBufferVector as Buffer
import numpy as np
from threading import Thread
import threading
import ProcessingModule.PM_Parameters as PM_Parameters
import time
import ProcessingModule.SynergyDetection as SD
import csv
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process
import scipy
import pymsgbox as msgbox
import csv
import json
import pandas as pd

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

    def LowPassFilter(self, signal):
        self.signal = np.roll(self.signal,1,axis=0)
        self.signal[0] = signal

        y = np.dot(self.b,self.signal)
        y = y - np.dot(self.a[1:],self.filtered_signal)
        y = y/self.a[0]

        self.filtered_signal = np.roll(self.filtered_signal,1,axis=0)
        self.filtered_signal[0] = y
        return y

    def CreateLPF(self, fs, MusclesNumber):
        self.b, self.a = scipy.signal.iirfilter(N = 2, Wn = [40], ftype = 'butter',fs= fs, btype='Lowpass')
        self.signal = np.zeros((len(self.b), MusclesNumber))
        self.filtered_signal = np.zeros((len(self.a)-1, MusclesNumber))

    def Set_LastOutputWeight(self, Weight):
        self.LastOutputWeight = Weight

    def MapActivation(self,matriz, data):
        return np.maximum(np.matmul(data.T, matriz).T,0)

    def UpdatePosition(self,synergyActivation, synergy_CursorMap):

        '''longitud_deseada = 8
        ceros_faltantes = longitud_deseada - len(synergyActivation)
        synergyActivation = np.pad(synergyActivation, ((0,0),(0, ceros_faltantes)), mode='constant')[0]
        left,right,up,down = synergy_CursorMap

        return np.array([synergyActivation[right]-synergyActivation[left],synergyActivation[up]-synergyActivation[down]])
        '''
        return np.ravel(np.matmul(synergyActivation,synergy_CursorMap))

DataProcessing = DataProcessing()

def Processing():
    # PM_DS.PM_DataStruct.circular_stack.reset_counter()
    # create buffer for synergies
    PM_DS.InitializeVisualizationBuffers()
    PM_Parameters.projectionMatrix = PM_Parameters.GenerateProjectionMatrix(PM_Parameters.synergy_CursorMap)
    
    counter = 0
    print("PM: Processing live")
    if PM_Parameters.saveCSV:
        FileName = 'ExperimentsFiles\Experiment-' + PM_Parameters.ExperimentTimestamp + "\RawData.csv"
        file = open(FileName, 'w', newline='')
        writer = csv.writer(file)
        writer.writerow([f'Muscle {i+1}' for i in range(PM_Parameters.MusclesNumber)])

    SubSamplingCounter = 0
    #ExecutionTime = []
    #t1 = 0
    #counter2 = 0

    
    while True:
        print("PM: Processing live")
        PM_DS.stack_lock.acquire()
        #ExecutionTime.append(time.time() - t1)
        RawData = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(1)
        #t1 = time.time()
        PM_DS.stack_lock.release()     
        SubSamplingCounter += 1
        counter += 1

        if RawData != []:
            
            if PM_Parameters.saveCSV:
                writer.writerow(RawData)
                file.flush()
            
            PM_Parameters.sampleCounter = PM_Parameters.sampleCounter + 1 
            RectifiedData = DataProcessing.Rectify(RawData)
            NormalizedData = DataProcessing.Normalize(RectifiedData, PM_Parameters.PeakActivation, PM_Parameters.MusclesNumber, PM_Parameters.Threshold)
            ProcessedData = DataProcessing.LowPassFilter(NormalizedData)
            reshapedData = ProcessedData.reshape(-1,1)
            
            PM_DS.SynergyBase_Semaphore.acquire()
            SynergyActivations = np.array(DataProcessing.MapActivation(PM_Parameters.SynergyBaseInverse,reshapedData).T)
            PM_DS.SynergyBase_Semaphore.release()
            
            if SubSamplingCounter > PM_Parameters.Subsampling_NumberOfSamples-1:
                print(counter)
                PM_DS.ProcessedDataBuffer_Semaphore.acquire()
                PM_DS.ProcessedDataBuffer.add_vector(ProcessedData)
                PM_DS.ProcessedDataBuffer_Semaphore.release()

                PM_DS.SynergiesBuffer_Semaphore.acquire()
                PM_DS.SynergiesBuffer.add_vector(SynergyActivations)
                PM_DS.SynergiesBuffer_Semaphore.release()
                SubSamplingCounter = 0
                
            NewMovement = DataProcessing.UpdatePosition(SynergyActivations, PM_Parameters.projectionMatrix).reshape(2,)

            PM_DS.PositionOutput_Semaphore.acquire()
            PM_DS.PM_DataStruct.positionOutput = PM_DS.PM_DataStruct.positionOutput + PM_Parameters.CursorMovement_Gain*NewMovement/PM_Parameters.sampleRate
            PM_DS.PositionOutput_Semaphore.release()
        
        # if counter2 > 3000:
            
        #     '''frame = pd.DataFrame(ExecutionTime).to_csv('./Processing_ExecTime.csv')
        #     #frame2 = pd.DataFrame(PM_DS.PM_DataStruct.circular_stack.get_counter()).to_csv('./Count.csv')
        #     msgbox.alert(PM_DS.PM_DataStruct.circular_stack.get_counter())'''
        #     # Create a DataFrame with ExecutionTime and the counter
        #     frame = pd.DataFrame({
        #         'ExecutionTime': ExecutionTime,
        #         'Counter': [PM_DS.PM_DataStruct.circular_stack.get_counter()] * len(ExecutionTime)  # Add the counter as a new column
        #     })

        #     # Save the DataFrame to a CSV file
        #     frame.to_csv('./Processing_ExecTime.csv', index=False)
        #     PM_DS.PM_DataStruct.circular_stack.reset_counter()
        #     counter2 = 0
        #     ExecutionTime = []
        # else: 
        #     counter2+=1
            

def CalibrationProcessing():

    while(PM_Parameters.Initialized == False):
       pass
    DataProcessing.CreateLPF(PM_Parameters.sampleRate, PM_Parameters.MusclesNumber)
    print("PM: Calibration Processing live")
    while not PM_Parameters.TerminateCalibration:

        print("PM: Calibration Processing live")

        if PM_Parameters.CalibrationStage == 1:
            print("Detecting Thresholds...")
            PM_DS.stack_lock.acquire()
            PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
            PM_DS.stack_lock.release()

            thresholds = np.zeros(PM_Parameters.MusclesNumber)
            #LastData = np.zeros((1,GlobalParameters.MusclesNumber))
            Peaks = [[] for _ in range(PM_Parameters.MusclesNumber)]

            while(PM_Parameters.CalibrationStage == 1):
                PM_DS.stack_lock.acquire()
                DataBatch = np.array(PM_DS.PM_DataStruct.circular_stack.get_vectors(1))
                PM_DS.stack_lock.release()
                
                if DataBatch != []:
                    RectifiedMuscleData = DataProcessing.Rectify(DataBatch)
                    for row in range(len(DataBatch)):
                        #DataBatch[row]= DataProcessing.DummyLowPassFilter(RectifiedMuscleData[row], LastData)
                        DataBatch[row]= DataProcessing.LowPassFilter(RectifiedMuscleData[row])
                        #LastData = RectifiedMuscleData[row]

                    for muscle in range(PM_Parameters.MusclesNumber):
                        Peaks[muscle].append(np.max(DataBatch[:,muscle]))
                print("stage1")
            for muscle in range(PM_Parameters.MusclesNumber):
                thresholds[muscle] = np.median(np.array(Peaks[muscle]))

            print("Thresholds:", thresholds)
            PM_Parameters.Threshold = thresholds*1.1
            PM_Parameters.PlotThresholds = True

        elif PM_Parameters.CalibrationStage == 2:
            print("Detecting Peaks...")
            PM_DS.stack_lock.acquire()
            PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
            PM_DS.stack_lock.release()

            #LastData = np.zeros((1,GlobalParameters.MusclesNumber))

            while(PM_Parameters.CalibrationStage == 2):
                PM_DS.stack_lock.acquire()
                RawData = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(1)
                #print("                                                                    ",RawData)
                PM_DS.stack_lock.release()
                if RawData != []:
                    RectifiedData = DataProcessing.Rectify(RawData)
                    #ProcessedData = DataProcessing.DummyLowPassFilter(RectifiedData, LastData).reshape(-1,1)
                    ProcessedData = DataProcessing.LowPassFilter(RectifiedData).reshape(-1,1)
                    #LastData = RectifiedData

                    for i in range(PM_Parameters.MusclesNumber):
                        if ProcessedData[i] > PM_Parameters.PeakActivation[i]:
                            PM_Parameters.PeakActivation[i] = ProcessedData[i]
                print("stage2")
            print("Peaks:", PM_Parameters.PeakActivation)
            PM_Parameters.PeakActivation = PM_Parameters.PeakActivation*0.9
            PM_Parameters.PlotPeaks = True

        elif PM_Parameters.CalibrationStage == 3:
            
            PM_Parameters.RequestCalibrationTime = True 
            while PM_Parameters.RequestCalibrationTime:
                pass
            print("Detecting Synergies...") 
            PM_DS.stack_lock.acquire()
            PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
            PM_DS.stack_lock.release()

            LastData = np.zeros((1,PM_Parameters.MusclesNumber))
            # Create an empty buffer with zeros
            aux_buffer = np.zeros((PM_Parameters.TimeCalibStage3*int(np.round(PM_Parameters.sampleRate)), PM_Parameters.MusclesNumber)) #Parametrizar el tamaño del buffer.

            while(PM_Parameters.CalibrationStage == 3):
                PM_DS.stack_lock.acquire()
                RawData = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(1)
                PM_DS.stack_lock.release()
                if RawData != []:
                    RectifiedData = DataProcessing.Rectify(RawData)
                    NormalizedData = DataProcessing.Normalize(RectifiedData, PM_Parameters.PeakActivation, PM_Parameters.MusclesNumber, PM_Parameters.Threshold)
                    ProcessedData = DataProcessing.DummyLowPassFilter(NormalizedData, LastData)
                    #ProcessedData = DataProcessing.LowPassFilter(NormalizedData)
                    LastData = NormalizedData

                    aux_buffer = np.roll(aux_buffer, -1, axis=0)    # Roll the buffer to make space for the new vector
                    aux_buffer[-1] = ProcessedData                  # Add the new vector at the end of the buffer
                print("stage3")
        
            PM_Parameters.DetectingSynergies = True
            try: 
                PM_Parameters.modelsList, PM_Parameters.vafs, PM_Parameters.output= SD.calculateSynergy(aux_buffer)
            except Exception as e:
                msgbox.alert(f"Cannot detect synergies: {e}")

            PM_Parameters.DetectingSynergies = False
            PM_Parameters.SynergyBase = PM_Parameters.output[1]
            PM_Parameters.SynergyBaseInverse = PM_Parameters.output[2]
            PM_Parameters.synergiesNumber = PM_Parameters.output[0]
            PM_Parameters.PlotSynergiesDetected = True
            del aux_buffer
      
        elif PM_Parameters.CalibrationStage == 4:
            PM_Parameters.UploadFromJson = True
            while PM_Parameters.CalibrationStage == 4:
                print("stage4")
                if PM_Parameters.JsonReceived:
                    PM_Parameters.JsonReceived = False 
                    try:
                        PM_Parameters.SynergyBaseInverse = np.linalg.pinv(PM_Parameters.SynergyBase)
                        PM_Parameters.projectionMatrix = PM_Parameters.GenerateProjectionMatrix(PM_Parameters.synergy_CursorMap)    
                    except Exception as e:
                        msgbox.alert(e)
                    break

        elif PM_Parameters.CalibrationStage == 5:
            print("stage5")
            PM_Parameters.UploadSimulationConfig = True
            PM_Parameters.CalibrationStage = 0            

            

    print("PM: Calibration terminated")
    PM_Processing.start()
    

PM_Calibration = Thread(target=CalibrationProcessing,daemon=True)
PM_Processing = Thread(target=Processing,daemon=True)
