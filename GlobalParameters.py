# In this file we will decalre the parametrs that will be used in the PM
import numpy as np
import csvHandler


ModoDelsys = True # True if we use the Delsys API Server, False if we use the API Server from the PM.
Initialized = False
getConfigurationFromCsv = True

MusclesNumber = 8
synergysNumber = MusclesNumber
RawData_BufferSize = 1000
sampleRate = 1

SynergyConfigurationFile = 'SynergyConfiguration.csv'

synergy_CursorMap = [0,1,0,1]
CursorMovement_Gain = 3

SynergyBase = np.identity(8)

PeakActivation = []
Noise = []

def Initialize():
    global SynergyBase 
    global PeakActivation 
    global Initialized

    if getConfigurationFromCsv:
        try:
            csvHandler.Read_csv(SynergyConfigurationFile, synergysNumber, MusclesNumber)
        except Exception as e:
            print(e)
    PeakActivation = np.ones(MusclesNumber) 
    
    Initialized = True

def Read_csv(csvfile):
    
    global synergy_CursorMap
    global SynergyBase

    left = [3, 10]
    rigth = [3,14]
    up = [1,12]
    down = [5,12]

    # Open the CSV file
    with open(csvfile, 'r') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile, delimiter=';')
        
        next(csv_reader)
        row = next(csv_reader)
        synergy_CursorMap[2] = row[up[1]]

        next(csv_reader)
        row = next(csv_reader)
        synergy_CursorMap[0] = row[left[1]]
        synergy_CursorMap[1] = row[rigth[1]]
        
        next(csv_reader)
        row = next(csv_reader)
        synergy_CursorMap[3] = row[down[1]]
        
        # Reset the reader's position to the beginning of the file
        csvfile.seek(0)     
        
        # Skip rows until reaching the start row
        next(csv_reader)
        next(csv_reader)
        
        for i in range(synergysNumber):
            row = next(csv_reader)
            for j in range(1,MusclesNumber+1):
                if row[j] == "":
                    raise Exception("Hay mas channels disponibles que musculos en la matriz de configuracion")
                if j == MusclesNumber and row[j+1]!="":
                    raise Exception("Hay mas musculos en la matriz que channels disponibles")
                SynergyBase[i, j-1] = float(row[j])
                
                
      