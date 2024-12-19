import csv
import time
from collections import deque
import numpy as np
from threading import Thread, Semaphore
import DataServer.API_Parameters as params
import pymsgbox as msgbox
frequency = params.SimulationFrequency  # Sample rate
#params.csvFile = 'Infinito.csv'  # CSV file
#params.csvFile = params.csvFile #'Data_Source.csv'

# Initialize global stack
stack = deque(maxlen = 1000)
stack_lock = Semaphore(1)  # Semaphore for stack access

# Create channels ID
channels = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']

class FormattedDictionary:
    def __init__(self, dictionary):
        self.dictionary=dictionary
        self.Keys=list(self.dictionary.keys())
    def __getitem__(self, key):
        return self.dictionary[key]
    
class channelObject:
    def __init__(self,name):
        self.Name = name + "EMG"
        self.SampleRate = 2148
        self.SamplesPerFrame = 1
        self.Id = name
    
class SensorsList:
    def __init__(self):
        self.SensorsList = []
        with open(params.csvFile, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            row = next(csv_reader)
            for channel in row:
                sensorInstance = SensorObject(channel)
                self.SensorsList.append(sensorInstance)     
            self.Result = self.SensorsList

class SensorObject:
    def __init__(self,sensorName):
        self.SensorName = sensorName
        self.TrignoChannels = [channelObject(sensorName)]
        
class AeroPyNuevo:
    def __init__(self):
        self.stop_flag = False
    
    def Start(self):
        start_thread = Thread(target=self.StartStreaming)
        start_thread.start()
    
    def StartStreaming(self):
        # Open CSV file
        with open(params.csvFile, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            # Skip the headers row
            next(csv_reader)
            # Read each row of csv file
            for row in csv_reader:
                stack_lock.acquire()  # Acquire lock before accessing the stack
                row = np.array(row, dtype=np.float64)  # Convert the row to numpy array
                stack.append(row)
                stack_lock.release()  # Release lock after modifying the stack
                # lock after modifying the stack
                time.sleep(1/frequency if frequency > 0 else 1)
                # Check if stop flag is set
                if self.stop_flag:
                    return
            print("There's no more data")

    def CheckDataQueue(self):
        # Check if there's new data in the internal buffer
        stack_lock.acquire()  # Acquire lock before accessing the stack
        data_available = len(stack) > 0
        stack_lock.release()  # Release lock after reading the stack
        
        return data_available

    def PollData(self):
        # Create the data dictionary
        if not self.CheckDataQueue(): 
            return FormattedDictionary({})
        data_dict = {}
        stack_lock.acquire()  # Acquire lock before accessing the stack
        # Get the data for each channel
        for channel in self.Channels:
            #Use the following line if you want to have pairs of data (time,sample) for each channel instead of the time as another channel
            channel_data = [row[self.Channels.index(channel)] for row in stack]
            data_dict[channel] = channel_data
        
        stack.clear()
        stack_lock.release()  # Release lock after reading and clearing the stack
        data=FormattedDictionary(data_dict)
        return data
    
    def Stop(self):
        self.stop_flag = True

    def ValidateBase(self,key, license):
        pass

    def GetPipelineState(self):
        return 'Connected'	
    
    def ScanSensors(self):
        self.SensorsList = SensorsList()
        self.NumberOfChannels = len(self.SensorsList.SensorsList)
        return self.SensorsList
        
    def GetSensorNames(self):
        self.Channels = []
        for i in range(len(self.SensorsList.SensorsList)):
            self.Channels.append(self.SensorsList.SensorsList[i].SensorName)
        return self.Channels
        
    def SelectAllSensors(self):
        pass

    def PairSensor(self):
        print("Pairing sensor")
        pass
    
    
    def GetSensorObject(self,i):
        
        return self.SensorsList.SensorsList[i] 
    
    def SetSampleMode(self,curSensor,setMode):
        pass

    def GetAllSampleModes(self):
        return ['EMG raw (2148Hz), +/-11mv, 10-850Hz' for i in range(self.NumberOfChannels)]
    
    def Configure(self):
        pass

aero_instance = AeroPyNuevo()
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
# Test 


def main():
    # Create an instance of the AeroPy class
    aero_instance = AeroPyNuevo()
    start_thread = Thread(target=aero_instance.Start)
    start_thread.start()

    while True:
        command = input("Enter a command (poll/stop): ")
        if command == "poll":

            DataOut = aero_instance.PollData()
            print(DataOut)
            python_dictionary = {}
            
            keys = []
            for i in DataOut.Keys:
                keys.append(i)
             
            for j in range(len(DataOut.Keys)):
                python_dictionary[keys[j]] = DataOut[keys[j]]
                
            print(python_dictionary)      
            print(python_dictionary[keys[0]]) 
                      
        elif command == "stop":
            aero_instance.Stop()
            # Perform any necessary cleanup or termination tasks
            break
        else:
            print("Invalid command. Try again.")


if __name__ == "__main__":
    main() 



