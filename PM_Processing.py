import PM_DataStructure as PM_DS
import numpy as np
from threading import Thread
import GlobalParameters
import time
import SynergyDetection as SD
import csv
import numpy as np
import matplotlib.pyplot as plt

plt.switch_backend('TkAgg')

# Function to save data to a CSV file
def save_to_csv(filename, aux_vector, M1, M2):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Thresholds', 'M1', 'M2'])
        for i in range(len(aux_vector)):
            writer.writerow([aux_vector[i], M1[i], M2[i]])

def PlotResults(Thresholds, ID):
    
    num_musculos = len(Thresholds)
    nombres_musculos = [f'Músculo {i+1}' for i in range(num_musculos)]  # Generar automáticamente los nombres de los músculos
    
    # Crear una figura y ejes para el gráfico de barras
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Graficar las barras
    ax.bar(nombres_musculos, Thresholds)  
    
    if ID == "Thresholds":

        ax.set_xlabel('Muscles')  # Etiqueta del eje x
        ax.set_ylabel('Thresholds')  # Etiqueta del eje y
        ax.set_title('Detected thresholds')  # Título del gráfico

    elif ID == "Peaks":
        ax.set_xlabel('Muscles')  # Etiqueta del eje x
        ax.set_ylabel('Peaks')  # Etiqueta del eje y
        ax.set_title('Detected Peaks')  # Título del gráfico

    else:
        return
    
    plt.show()

def PlotSynergiesDetected(vafs, knee_point, H):
    # Plot VAF data
    x = list(range(2, GlobalParameters.MusclesNumber+1))  # Number of muscles
    plt.plot(x, vafs, marker='o', label='VAF Curve')
    plt.xlabel('Number of Synergies')
    plt.ylabel('VAF')
    plt.title('VAF vs Number of Synergies')

    # Plot knee point
    plt.axvline(x=knee_point, color='red', linestyle='--', label='Knee Point')
    plt.legend()

    # Annotate knee point
    plt.text(knee_point + 0.1, max(vafs) - 0.05, f'Knee Point: {knee_point}', color='red')

    # Show plot
    plt.show()

    # Bars graphic of synergies 
    aux= []
    plt.figure()
    #plt.subplot(111)
    #plt.plot(range(2,GlobalParameters.MusclesNumber+1), vafs)
    #plt.figure()

    for j in range(0, knee_point):   
        plt.subplot(100*knee_point+10+j+1)
        for i in range(0, H.shape[1]):
            aux.append(np.max(H[j,i]))
        plt.bar(range(0,GlobalParameters.MusclesNumber), aux)
        aux = []
    
    plt.show()



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

    def UpdatePosition(self,synergyActivation, synergy_CursorMap):
        
        '''longitud_deseada = 8
        ceros_faltantes = longitud_deseada - len(synergyActivation)
        synergyActivation = np.pad(synergyActivation, ((0,0),(0, ceros_faltantes)), mode='constant')[0]
        left,right,up,down = synergy_CursorMap

        return np.array([synergyActivation[right]-synergyActivation[left],synergyActivation[up]-synergyActivation[down]])
        '''
        return np.ravel(np.matmul(synergyActivation,synergy_CursorMap))
        
        
DataProcessing = DataProcessing()
LastRawData = [0 for i in range(GlobalParameters.MusclesNumber)]

def Processing():
    
    GlobalParameters.projectionMatrix = GlobalParameters.GenerateProjectionMatrix(GlobalParameters.synergy_CursorMap)
    LastNormalizedData = [0 for i in range(GlobalParameters.MusclesNumber)]
   
    while True:
        print("PM: Processing live")
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
           
            #NewMovement = DataProcessing.UpdatePosition(SynergyActivations, GlobalParameters.synergy_CursorMap)
            NewMovement = DataProcessing.UpdatePosition(SynergyActivations, GlobalParameters.projectionMatrix).reshape(2,)
            #print(NewMovement)
            PM_DS.PositionOutput_Semaphore.acquire()
            PM_DS.PM_DataStruct.positionOutput = PM_DS.PM_DataStruct.positionOutput + GlobalParameters.CursorMovement_Gain*NewMovement/GlobalParameters.sampleRate
            PM_DS.PositionOutput_Semaphore.release()


def CalibrationProcessing():
    
    while(GlobalParameters.Initialized == False):
       pass

    while not GlobalParameters.TerminateCalibration:
        print("PM: Calibration Processing live")
        
        if GlobalParameters.CalibrationStage == 1:
            print("Detecting Thresholds...")
            PM_DS.stack_lock.acquire()
            PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
            PM_DS.stack_lock.release()

            GlobalParameters.Threshold = np.ones(GlobalParameters.MusclesNumber) * 0.055

            thresholds = np.zeros(GlobalParameters.MusclesNumber)
            LastData = [0 for i in range(GlobalParameters.MusclesNumber)]
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

            for muscle in range(GlobalParameters.MusclesNumber):
                thresholds[muscle] = np.median(np.array(Peaks[muscle]))
            
            print("Thresholds:", thresholds)
            GlobalParameters.Threshold = thresholds
            PlotResults(GlobalParameters.Threshold, "Thresholds")
            
        elif GlobalParameters.CalibrationStage == 2:
            print("Detecting Peaks...")
            PM_DS.stack_lock.acquire()
            PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
            PM_DS.stack_lock.release()

            GlobalParameters.PeakActivation = np.ones(GlobalParameters.MusclesNumber)*0.1 

            LastData = [0 for i in range(GlobalParameters.MusclesNumber)]

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
            PlotResults(GlobalParameters.PeakActivation, "Peaks")
            
        elif GlobalParameters.CalibrationStage == 3:
            print("Detecting Synergies...")
            PM_DS.stack_lock.acquire()
            PM_DS.PM_DataStruct.circular_stack.get_vectors(1)
            PM_DS.stack_lock.release()

            LastData = [0 for i in range(GlobalParameters.MusclesNumber)]
            # Create an empty buffer with zeros
            aux_buffer = np.zeros((10*2000, GlobalParameters.MusclesNumber)) #Parametrizar el tamaño del buffer.

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

            (n_components, H, r_squared, vaf), vafs = SD.calculateSynergy(aux_buffer)
            print(n_components, H, r_squared, vaf)
            #SD.BarsGraphic(n_components, H, r_squared, vafs)
            GlobalParameters.synergiesNumber = n_components
            GlobalParameters.SynergyBase = H
            GlobalParameters.SynergyBaseInverse = np.linalg.pinv(H)   
            PlotSynergiesDetected(vafs, n_components, H)
            GlobalParameters.RequestAngles = True
            GlobalParameters.AnglesRecieved = False
            while not GlobalParameters.AnglesRecieved:
                pass

            print(GlobalParameters.synergy_CursorMap)  
    print("PM: Calibration terminated")          
    # Plot the vectors
    