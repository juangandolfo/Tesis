import csv
import numpy as np

class ExperimentData:
    def __init__(self, SynergyBase, Synergy_CursorMap, PeakActivation, Noise):
        self.SynergyBase = SynergyBase
        self.Synergy_CursorMap = Synergy_CursorMap
        self.PeakActivation = PeakActivation
        self.Noise = Noise


def SaveExperimentConfiguration(data, filename):
    fieldnames = ['SynergyBase', 'Synergy_CursorMap', 'PeakActivation', 'Noise']
    
    
    with open(filename + ".csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({'SynergyBase': data.SynergyBase,
                         'Synergy_CursorMap': data.Synergy_CursorMap,
                         'PeakActivation': data.PeakActivation,
                         'Noise': data.Noise})
    
# Create an instance of ExperimentData
data = ExperimentData(np.identity(8), np.array([1, 2]), np.array([3, 4]), np.array([5, 6]))

# Call the function with the instance of ExperimentData
SaveExperimentConfiguration(data, "Experiment1")

def Read_csv(csvfile):
    synergy_CursorMap = []
    SynergyBase = []
    # Open the CSV file
    with open(csvfile, 'r') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile, delimiter=',')
        row = np.array(next(csv_reader), dtype=float)
        MusclesNumber = len(row)
        while(row[0] != ''):
            '''np.zeros(MusclesNumber).any()):'''
            
            SynergyBase.append(row)  
            print(SynergyBase)
            a = next(csv_reader)
            print(a)
            row = np.array(a, dtype=float)
        print(1)
            
        row = next(csv_reader)
        SynergyBase.append((np.array(row, dtype=float)))  
        print(SynergyBase) 

        '''while(row != ""):
            row = next(csv_reader)
            for j in range(1,MusclesNumber+1):
                if row[j] == "":
                    raise Exception("Hay mas channels disponibles que musculos en la matriz de configuracion")
                if j == MusclesNumber and row[j+1]!="":
                    raise Exception("Hay mas musculos en la matriz que channels disponibles")
                SynergyBase[i, j-1] = float(row[j])'''


'''def Read_csv(csvfile, synergysNumber, MusclesNumber):
    
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
'''


filename = "SynergyConfigurationFromExcel.csv"
Read_csv(filename)
