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
        # get the first row
        StrRow = next(csv_reader)   
        row = np.array(StrRow, dtype=float) 
        # get the number of muscles
        MusclesNumber = len(row)
        #create the null row for comparison
        NullRow = ['' for _ in range(MusclesNumber)]
        SynergiesNumber = 0
        while(StrRow != NullRow):
            row = np.array(StrRow, dtype=float)
            SynergyBase.append(row)
            StrRow = next(csv_reader)
            SynergiesNumber += 1
        
        SynergyBase = np.matrix(SynergyBase)
        
        strRow = next(csv_reader)
        synergy_CursorMap = np.array(strRow[0].strip('[]').split(','), dtype=int)
        
        
        return SynergyBase, synergy_CursorMap, MusclesNumber, SynergiesNumber

   