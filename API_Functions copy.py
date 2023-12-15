import csv
import time
from collections import deque
import numpy as np
from threading import Thread, Semaphore


frequency = 2 # Sample rate
csv_file = 'Sinusoidales.csv'  # CSV file

# Initialize global stack
stack = []
stack_lock = Semaphore(1)  # Semaphore for stack access

# Create channels ID
channels = ['t', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']

# Flag variable to indicate whether to stop the start() function
stop_flag = False

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def Start():
    
    # Open CSV file
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        #print(csv_reader)

        # Skip the headers row
        next(csv_reader)

        # Read each row of csv file
        for row in csv_reader:
            stack_lock.acquire()  # Acquire lock before accessing the stack
            row = np.array(row, dtype=np.float64)  # Convert the row to numpy array
            # row = [int(item) for item in row] , to avoid use numpy
            stack.append(row)
            stack_lock.release()  # Release lock after modifying the stack
            # lock after modifying the stack
            
            time.sleep(1/frequency)
            # Check if stop flag is set
            if stop_flag:
                return
        
        print("There's no more data")
        

# Option B        
"""data = np.genfromtxt(csv_file, delimiter=';', skip_header=1, dtype=np.float64)
    for row in data:
        stack_lock.acquire()  # Acquire lock before accessing the stack
        stack.append(row)
        stack_lock.release()  # Release lock after modifying the stack
        print(row)
        time.sleep(1/frequency)

        # Check if stop flag is set
        if stop_flag:
            return
        
    print("There's no more data")"""



#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def CheckDataQueue():
    # Check if there's new data in the internal buffer
    stack_lock.acquire()  # Acquire lock before accessing the stack
    data_available = len(stack) > 0
    stack_lock.release()  # Release lock after reading the stack
    return data_available

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
class FormattedDictionary:
    def __init__(self, dictionary):
        self.dictionary=dictionary
        self.Keys=list(self.dictionary.keys())
    def __getitem__(self, key):
        return self.dictionary[key]
    
  


def PollData():
    if not CheckDataQueue():
        #return {'t':[0], 'M1':[0], 'M2':[0], 'M3':[0], 'M4':[0], 'M5':[0], 'M6':[0], 'M7':[0], 'M8':[0]}
        return {}

    # Create the data dictionary
    data_dict = {}

    stack_lock.acquire()  # Acquire lock before accessing the stack
    # Get the data for each channel
    for channel in channels:
        #Use the following line if you want to have pairs of data (time,sample) for each channel instead of the time as another channel
        #channel_data = [[row[0], row[channels.index(channel) + 1]] for row in stack]
        channel_data = [row[channels.index(channel)] for row in stack]
        data_dict[channel] = channel_data

    stack.clear()
    stack_lock.release()  # Release lock after reading and clearing the stack
    
    data=FormattedDictionary(data_dict)
    
    return data
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def Stop():
    global stop_flag
    stop_flag = True

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

# Test 

'''
def main():
    start_thread = Thread(target=Start)
    start_thread.start()

    while True:
        command = input("Enter a command (poll/stop): ")
        if command == "poll":
            data = PollData()
            print(data.dictionary)          
                      
        elif command == "stop":
            Stop()
            # Perform any necessary cleanup or termination tasks
            break
        else:
            print("Invalid command. Try again.")


if __name__ == "__main__":
    main() 
'''




'''
class AeroPy:
    def __init__(self, frequency, csv_file, channels):
        self.frequency = frequency
        self.csv_file = csv_file
        self.channels = channels
        self.stack = deque()
        self.stack_lock = Semaphore(1)  # Semaphore for stack access
        self.stop_flag = False

    def start(self):
        with open(self.csv_file, 'r') as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader)  # Skip the headers row

            for row in csv_reader:
                self.stack_lock.acquire()
                row = np.array(row, dtype=np.float64)
                self.stack.append(row)
                self.stack_lock.release()

                time.sleep(1 / self.frequency)

                if self.stop_flag:
                    print("Stopping...")
                    return

            print("There's no more data")

    def check_data_queue(self):
        self.stack_lock.acquire()
        data_available = len(self.stack) > 0
        self.stack_lock.release()
        return data_available

    def poll_data(self):
        if not self.check_data_queue():
            return {}

        data_dict = {}
        self.stack_lock.acquire()

        for channel in self.channels:
            channel_data = [row[self.channels.index(channel)] for row in self.stack]
            data_dict[channel] = channel_data

        self.stack.clear()
        self.stack_lock.release()

        data = FormattedDictionary(data_dict)

        return data

    def stop(self):
        self.stop_flag = True

class FormattedDictionary:
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.keys = list(self.dictionary.keys())

    def __getitem__(self, key):
        return self.dictionary[key]

# Ejemplo de uso
frequency = 2
csv_file = 'Sinusoidales.csv'
channels = ['t', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']

aero_instance = AeroPy(frequency, csv_file, channels)

# Inicia el hilo para la lectura de datos
start_thread = Thread(target=aero_instance.start)
start_thread.start()

# Hacer otras operaciones o tareas aquí

# Luego, puedes llamar a las otras funciones según sea necesario
while True:
    command = input("Enter a command (poll/stop): ")
    if command == "poll":
        data = aero_instance.poll_data()
        print(data.keys)  # Accede a las keys del FormattedDictionary
        print(data['t'])  # Accede a la data correspondiente a la key 't'
    elif command == "stop":
        aero_instance.stop()
        break
    else:
        print("Invalid command. Try again.")'''