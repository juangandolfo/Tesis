import PM_DataStructure as PM_DS
import LocalCircularBufferVector as Buffer
import numpy as np
from threading import Thread
import GlobalParameters
import time
import SynergyDetection as SD
import csv
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process
import scipy
import pymsgbox as msgbox
import csv
import json

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
        self.b, self.a = scipy.signal.iirfilter(N = 2, Wn = [10], ftype = 'butter',fs= fs, btype='Lowpass')
        self.signal = np.zeros((len(self.b), MusclesNumber))
        self.filtered_signal = np.zeros((len(self.a)-1, MusclesNumber))

    def Set_LastOutputWeight(self, Weight):
        self.LastOutputWeight = Weight

    def MapActivation(self,matriz, data):
        return np.matmul(data.T, matriz).T

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
    # create buffer for synergies
    PM_DS.InitializeVisualizationBuffers()
    GlobalParameters.projectionMatrix = GlobalParameters.GenerateProjectionMatrix(GlobalParameters.synergy_CursorMap)
    DataProcessing.CreateLPF(GlobalParameters.sampleRate, GlobalParameters.MusclesNumber)
    #LastNormalizedData = [0 for i in range(GlobalParameters.MusclesNumber)]
    processedSum = 0
    counter = 0
    print("PM: Processing live")
    if GlobalParameters.saveCSV:
        today = time.gmtime()
        FileName = './Experiments/Experiment-' + GlobalParameters.ExperimentTimestamp + ".csv"
        file = open(FileName, 'w', newline='')
        writer = csv.writer(file)
        writer.writerow([f'Muscle {i+1}' for i in range(GlobalParameters.MusclesNumber)])
    while True:
        print("PM: Processing live")
        PM_DS.stack_lock.acquire()
        RawData = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(1)
        PM_DS.stack_lock.release()     

        if RawData != []:
            
            if GlobalParameters.saveCSV:
                writer.writerow(RawData)
                file.flush()

            RectifiedData = DataProcessing.Rectify(RawData)
            ProcessedData = DataProcessing.LowPassFilter(RectifiedData)
            NormalizedData = DataProcessing.Normalize(ProcessedData, GlobalParameters.PeakActivation, GlobalParameters.MusclesNumber, GlobalParameters.Threshold)
            #ProcessedData = DataProcessing.DummyLowPassFilter(NormalizedData, LastNormalizedData)
            reshapedData = NormalizedData.reshape(-1,1)
            #LastNormalizedData = NormalizedData

            PM_DS.ProcessedDataBuffer_Semaphore.acquire()
            PM_DS.ProcessedDataBuffer.add_vector(ProcessedData)
            PM_DS.ProcessedDataBuffer_Semaphore.release()


            PM_DS.SynergyBase_Semaphore.acquire()
            SynergyActivations = np.array(DataProcessing.MapActivation(GlobalParameters.SynergyBaseInverse,reshapedData).T)
            PM_DS.SynergyBase_Semaphore.release()

            PM_DS.SynergiesBuffer_Semaphore.acquire()
            PM_DS.SynergiesBuffer.add_vector(SynergyActivations)
            PM_DS.SynergiesBuffer_Semaphore.release()

            NewMovement = DataProcessing.UpdatePosition(SynergyActivations, GlobalParameters.projectionMatrix).reshape(2,)

            PM_DS.PositionOutput_Semaphore.acquire()
            PM_DS.PM_DataStruct.positionOutput = PM_DS.PM_DataStruct.positionOutput + GlobalParameters.CursorMovement_Gain*NewMovement/GlobalParameters.sampleRate
            PM_DS.PositionOutput_Semaphore.release()



def CalibrationProcessing():

    while(GlobalParameters.Initialized == False):
       pass

    print("PM: Calibration Processing live")
    while not GlobalParameters.TerminateCalibration:

        print("PM: Calibration Processing live")

        if GlobalParameters.CalibrationStage == 1:
            print("Detecting Thresholds...")
            PM_DS.stack_lock.acquire()
            PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
            PM_DS.stack_lock.release()

            thresholds = np.zeros(GlobalParameters.MusclesNumber)
            LastData = np.zeros((1,GlobalParameters.MusclesNumber))
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

                    for muscle in range(GlobalParameters.MusclesNumber):
                        Peaks[muscle].append(np.max(DataBatch[:,muscle]))
                print("stage1")
            for muscle in range(GlobalParameters.MusclesNumber):
                thresholds[muscle] = np.median(np.array(Peaks[muscle]))

            print("Thresholds:", thresholds)
            GlobalParameters.Threshold = thresholds
            GlobalParameters.PlotThresholds = True

        elif GlobalParameters.CalibrationStage == 2:
            print("Detecting Peaks...")
            PM_DS.stack_lock.acquire()
            PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
            PM_DS.stack_lock.release()

            LastData = np.zeros((1,GlobalParameters.MusclesNumber))

            while(GlobalParameters.CalibrationStage == 2):
                PM_DS.stack_lock.acquire()
                RawData = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(1)
                #print("                                                                    ",RawData)
                PM_DS.stack_lock.release()
                if RawData != []:
                    RectifiedData = DataProcessing.Rectify(RawData)
                    ProcessedData = DataProcessing.DummyLowPassFilter(RectifiedData, LastData).reshape(-1,1)
                    LastData = RectifiedData

                    for i in range(GlobalParameters.MusclesNumber):
                        if ProcessedData[i] > GlobalParameters.PeakActivation[i]:
                            GlobalParameters.PeakActivation[i] = ProcessedData[i]
                print("stage2")
            print("Peaks:", GlobalParameters.PeakActivation)
            GlobalParameters.PlotPeaks = True

        elif GlobalParameters.CalibrationStage == 3:
            
            GlobalParameters.RequestCalibrationTime = True 
            while GlobalParameters.RequestCalibrationTime:
                pass
            print("Detecting Synergies...") 
            PM_DS.stack_lock.acquire()
            PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
            PM_DS.stack_lock.release()

            LastData = np.zeros((1,GlobalParameters.MusclesNumber))
            # Create an empty buffer with zeros
            aux_buffer = np.zeros((GlobalParameters.TimeCalibStage3*int(np.round(GlobalParameters.sampleRate)), GlobalParameters.MusclesNumber)) #Parametrizar el tamaño del buffer.

            while(GlobalParameters.CalibrationStage == 3):
                PM_DS.stack_lock.acquire()
                RawData = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(1)
                PM_DS.stack_lock.release()
                if RawData != []:
                    RectifiedData = DataProcessing.Rectify(RawData)
                    NormalizedData = DataProcessing.Normalize(RectifiedData, GlobalParameters.PeakActivation, GlobalParameters.MusclesNumber, GlobalParameters.Threshold)
                    ProcessedData = DataProcessing.DummyLowPassFilter(NormalizedData, LastData)
                    LastData = NormalizedData

                    aux_buffer = np.roll(aux_buffer, -1, axis=0)    # Roll the buffer to make space for the new vector
                    aux_buffer[-1] = ProcessedData                  # Add the new vector at the end of the buffer
                print("stage3")
        
            GlobalParameters.DetectingSynergies = True
            try: 
                GlobalParameters.modelsList, GlobalParameters.vafs, GlobalParameters.output= SD.calculateSynergy(aux_buffer)
            except Exception as e:
                msgbox.alert("Cannot detect synergies")

            GlobalParameters.DetectingSynergies = False
            GlobalParameters.SynergyBase = GlobalParameters.output[1]
            GlobalParameters.SynergyBaseInverse = GlobalParameters.output[2]
            GlobalParameters.synergiesNumber = GlobalParameters.output[0]
            GlobalParameters.PlotSynergiesDetected = True
            del aux_buffer
      
        elif GlobalParameters.CalibrationStage == 4:
            GlobalParameters.UploadFromJson = True
            while GlobalParameters.CalibrationStage == 4:
                print("stage4")
                if GlobalParameters.JsonReceived:
                    GlobalParameters.JsonReceived = False 
                    try:
                        GlobalParameters.SynergyBaseInverse = np.linalg.pinv(GlobalParameters.SynergyBase)
                        GlobalParameters.projectionMatrix = GlobalParameters.GenerateProjectionMatrix(GlobalParameters.synergy_CursorMap)    
                    except Exception as e:
                        msgbox.alert(e)
                    
                    GlobalParameters.UploadedFromJson = False
                    break

    print("PM: Calibration terminated")
    PM_Processing.start()

PM_Calibration = Thread(target=CalibrationProcessing,daemon=True)
PM_Processing = Thread(target=Processing,daemon=True)
