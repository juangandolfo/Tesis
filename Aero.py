import csv
import time
from collections import deque
import numpy as np
from threading import Thread, Semaphore

frequency = 3 # Sample rate
#csv_file = 'Infinito.csv'  # CSV file
csv_file = 'Data_Source.csv'

# Initialize global stack
stack = []
stack_lock = Semaphore(1)  # Semaphore for stack access

# Create channels ID
channels = ['t', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']

class FormattedDictionary:
    def __init__(self, dictionary):
        self.dictionary=dictionary
        self.Keys=list(self.dictionary.keys())
    def __getitem__(self, key):
        return self.dictionary[key]

class AeroPy:
    def __init__(self):
        self.stop_flag = False
    
    def Start(self):
        start_thread = Thread(target=self.StartStreaming)
        start_thread.start()
    
    def StartStreaming(self):
        # Open CSV file
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file, delimiter=';')
            # Skip the headers row
            next(csv_reader)
            # Read each row of csv file
            for row in csv_reader:
                stack_lock.acquire()  # Acquire lock before accessing the stack
                row = np.array(row, dtype=np.float64)  # Convert the row to numpy array
                stack.append(row)
                stack_lock.release()  # Release lock after modifying the stack
                # lock after modifying the stack
                
                time.sleep(1/frequency)
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
        for channel in channels[1:]:
            #Use the following line if you want to have pairs of data (time,sample) for each channel instead of the time as another channel
            channel_data = [row[channels.index(channel)] for row in stack]
            data_dict[channel] = channel_data
        stack.clear()
        stack_lock.release()  # Release lock after reading and clearing the stack
        data=FormattedDictionary(data_dict)
        return data
    
    def Stop(self):
        self.stop_flag = True


aero_instance = AeroPy()
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
# Test 


def main():
    # Create an instance of the AeroPy class
    aero_instance = AeroPy()
    start_thread = Thread(target=aero_instance.Start)
    start_thread.start()

    while True:
        command = input("Enter a command (poll/stop): ")
        if command == "poll":
            data = aero_instance.PollData()
            data2 = aero_instance.PollData()
            print(data.dictionary)         
                      
        elif command == "stop":
            aero_instance.Stop()
            # Perform any necessary cleanup or termination tasks
            break
        else:
            print("Invalid command. Try again.")


if __name__ == "__main__":
    main() 



