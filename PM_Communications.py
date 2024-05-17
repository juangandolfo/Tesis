import GlobalParameters
import PM_DataStructure as PM_DS
import socket
import json
import time
import pickle
import numpy as np
from threading import Thread




HOST = "127.0.0.1"  # Standard adress (localhost)
PORT_Client = 6001  # Port to get data from the File API Server
PORT_Server = 6002 # The port used by the PM Server


# Create a socket for the client 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Create a socket for the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Link the socket to the IP and PORT selected: 
server_socket.bind((HOST, PORT_Server))


# Auxiliar functions -------------------------------------------------------------------------------------------------------------------------------------------------------------

def Dictionary_to_matrix(dictionary):
    
    # Get the keys
    columns = list(dictionary.keys())
    # Get the data 
    rows = [dictionary[column] for column in columns]

    # Check if all rows have the same length 
    row_lengths = set(len(row) for row in rows)

    if len(row_lengths) > 1:
        
        # Find the minimum length
        min_length = min(row_lengths)
        # Trim rows to the minimum length
        rows = [row[:min_length] for row in rows]
        print("Trimmed data")
        

    # Create the matrix    
    matriz = np.array(rows).T 
          
    return matriz

# Function to send the request and receive the data from API Server
def Request(Type):
    request = "GET /"+Type
    client_socket.sendall(request.encode())
    
    data = b''       
    while True:
        try:
            client_socket.settimeout(0.5)
            chunk = client_socket.recv(1024)
            data += chunk
            if b"~" in data:
                #print("Delimiter found")
                break  # Delimiter found
            elif b"TC" in data: 
                GlobalParameters.TerminateCalibration = True
                break
            
            elif b"CS1" in data: 
                GlobalParameters.CalibrationStage = 1
                break
            elif b"CS2" in data: 
                GlobalParameters.CalibrationStage = 2
                break
            elif b"CS3" in data: 
                GlobalParameters.CalibrationStage = 3
                break
            elif b"CSF" in data: 
                GlobalParameters.CalibrationStage = 0
                break
            
        except socket.timeout as e:
            print(e)
            continue
        
        except socket.error as e:
            print(e)
            continue

    serialized_data = data.decode().rstrip("~") # Quit the delimiter and decode the received data
    response_data = json.loads(serialized_data) # Get the original data 
    #print(response_data)  
     
    if response_data == {}:
        raise Exception("PM:No data received")
    return response_data

# Function to handle the connection with a client
def Handle_Client(conn,addr):
    print(f"Connected by {addr}")
    #Connected = True
    while True:
        #print("PM Server live")
        data = conn.recv(1024)
        # Check if the received data is a GET request for "/data"
        if  data.decode().strip() == "GET /data1":
            #PM_DS.stack_lock.acquire()  # Acquire lock before accessing the stack
            #response_data = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(1)
            #print(response_data)
            #PM_DS.stack_lock.release()  # Release lock after reading the stack

            PM_DS.PositionOutput_Semaphore.acquire()
            response_data = GlobalParameters.CursorMovement_Gain*PM_DS.PM_DataStruct.positionOutput
            PM_DS.PM_DataStruct.positionOutput = np.zeros(2)
            PM_DS.PositionOutput_Semaphore.release()

            if response_data == []:
                print("Empty data")
                response_data = [0 for i in range(GlobalParameters.MusclesNumber)]
                         
            response_data = np.array(response_data).tolist()
            #print(response_data)
            response_json = json.dumps(response_data).encode()  # Convert the dictionary to JSON and enconde into bytes
            conn.sendall(response_json)
            #print("PM: Data sent:", response_data)
            

        elif  data.decode().strip() == "GET /data2":
            PM_DS.stack_lock.acquire()  # Acquire lock before accessing the stack
            response_data = PM_DS.PM_DataStruct.circular_stack.get_oldest_vector(2)
            #print(response_data)
            PM_DS.stack_lock.release()  # Release lock after reading the stack
            
            if response_data == []:
                response_data = [0 for i in range(GlobalParameters.MusclesNumber)]

            response_data = np.array(response_data).tolist()
            response_json = json.dumps(response_data).encode()  # Convert the dictionary to JSON and enconde intio bytes
            conn.sendall(response_json)
            #print("Data sent:", response_data)
        
        #if data.decode().strip() == "DISCONNECT":
             #Connected = False

        else:
            print("Invalid request") 
    #conn.close()                        
        
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Threads -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               
def Processing_Module_Client():
    client_socket.connect((HOST, PORT_Client))
    print("PM Client live")
    
    # Request Number of cahnnels from host
    GlobalParameters.MusclesNumber = Request("SensorsNumber")
    GlobalParameters.sampleRate = Request("SampleRate")
    try:
        GlobalParameters.Initialize()
    except Exception as e:
        print(e)
        return
        
    #print(GlobalParameters.MusclesNumber)
    PM_DS.PM_DataStruct.InitializeRawDataBuffer()
    #finger dance logic for calibration
    #GlobalParameters.SynergyBase = GetSynergyBase()

    # Loop to request data
    while True:
        #print("PM Client live")
        try:
            try:
                if GlobalParameters.RequestAngles == True:
                    data = Request("Angles")
                    print("Angles")
                    angles = []
                    if data != []:
                        for element in data:
                             # Check if the element is not '0'
                            if element != '':
                                # If it's not '0', add it to the result
                                angles.append(int(element))
                        GlobalParameters.synergy_CursorMap = angles
                        GlobalParameters.AnglesRecieved = True
                        GlobalParameters.RequestAngles = False
                        Request("data")
                        #Request("Erase stack")

                else:
                    data = Request("data")
                    formated_data = Dictionary_to_matrix(data)
                    PM_DS.stack_lock.acquire()  # Acquire lock before accessing the stack
                    PM_DS.PM_DataStruct.circular_stack.add_matrix(formated_data)
                    PM_DS.stack_lock.release()  # Release lock after reading the stack
                    
            except Exception as e:
                #print(e)
                continue
        except socket.error as e:
            print("Connection error:", e)
            continue
            # Manage a connection error 


def Processing_Module_Server():

    # Listen the inner connections:
    print("Server listening on", HOST, "port", PORT_Server)
    server_socket.listen()
    Num_Clients = 0
    
    while Num_Clients < 2:
        # Accept the connection and open a thread to handle the client. 
        conn, addr = server_socket.accept()
        thread = Thread(target = Handle_Client, args=(conn, addr))
        thread.start()
        Num_Clients = Num_Clients + 1
        #print(Num_Clients)

                    
    



