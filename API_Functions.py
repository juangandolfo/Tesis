import csv
import time
from collections import deque
import numpy as np
from threading import Thread, Semaphore

frequency = 2000 # Sample rate
csv_file = 'Data_Source.csv'  # CSV file

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

def PollData():
    if not CheckDataQueue():
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
    
    return data_dict
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def Stop():
    global stop_flag
    stop_flag = True

#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

# Test 

''''
def main():
    start_thread = Thread(target=Start)
    start_thread.start()

    while True:
        command = input("Enter a command (poll/stop): ")
        if command == "poll":
            data = PollData()
            print(data)
        elif command == "stop":
            Stop()
            # Perform any necessary cleanup or termination tasks
            break
        else:
            print("Invalid command. Try again.")


if __name__ == "__main__":
    main() '''