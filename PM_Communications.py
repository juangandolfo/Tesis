import GlobalParameters
import PM_DataStructure as PM_DS
import socket
import json
import time
import pickle
import numpy as np
from threading import Thread
import LocalCircularBufferVector as Buffer
import pymsgbox as msgbox



HOST = "127.0.0.1"  # Standard adress (localhost)
PORT_Client = 6001  # Port to get data from the File API Server
PORT_Server = 6002 # The port used by the PM Server


# Create a socket for the client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Create a socket for the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Link the socket to the IP and PORT selected:
#server_socket.bind((HOST, PORT_Server))

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
    #print("                                                                     Request:", request)
    try:
        client_socket.sendall(request.encode())
    except socket.error as e:
            print("PM request:", e)
    data = b''
    while True:
        try:
            chunk = client_socket.recv(1024)
            data += chunk
            if b"~" in data:
                serialized_data = data.decode().rstrip("~")
                break
            elif b"TC" in data:
                GlobalParameters.TerminateCalibration = True
                serialized_data = data.decode().rstrip("TC")
                break
            elif b"CS1" in data:
                GlobalParameters.CalibrationStage = 1
                serialized_data = data.decode().rstrip("CS1")
                break
            elif b"CS2" in data:
                GlobalParameters.CalibrationStage = 2
                serialized_data = data.decode().rstrip("CS2")
                break
            elif b"CS3" in data:
                GlobalParameters.CalibrationStage = 3
                serialized_data = data.decode().rstrip("CS3")
                break
            elif b"CSF" in data:
                GlobalParameters.CalibrationStage = 0
                serialized_data = data.decode().rstrip("CSF")
                break

        except socket.timeout as e:
            print("PM Client timeout", e)
            continue
        except socket.error as e:
            print("PM Client socket error", e)
            continue

    response_data = json.loads(serialized_data)
    if response_data == {}:
        #raise Exception("PM:No data received")
        pass
    return response_data

# Function to handle the connection with a client
def Handle_Client(conn,addr):

    print(f"Connected by {addr}")
    conn.settimeout(3)
    try:
        while True:
            #print("                                                      PM Server live")
            try:
                data = conn.recv(1024)
                if not data:
                    # No data received, client has likely disconnected
                    print(f"Client {addr} disconnected")
                    break

                # Check if the received data is a GET request for "/data"
                if  data.decode().strip() == "GET /data1":
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

                elif  data.decode().strip() == "GET /Muscles":

                    PM_DS.ProcessedDataBuffer_Semaphore.acquire()  # Acquire lock before accessing the stack
                    response_data = PM_DS.ProcessedDataBuffer.get_vectors(1)
                    PM_DS.ProcessedDataBuffer_Semaphore.release()  # Release lock after reading the stack

                    if response_data == []:
                        print("Empty data")
                        response_data = []


                    response_data = np.array(response_data).tolist()
                    response_json = json.dumps(response_data)
                    response_json  += "~" # Add a delimiter at the end
                    # Convert the dictionary to JSON and enconde intio bytes
                    conn.sendall(response_json.encode())
                    #print("Data sent:", response_data)

                elif data.decode().strip() == "GET /Synergies":

                        PM_DS.SynergiesBuffer_Semaphore.acquire()  # Acquire lock before accessing the stack
                        response_data = PM_DS.SynergiesBuffer.get_vectors(1) #PM_DS.PM_DataStruct.circular_stack.get_vectors(3)
                        PM_DS.SynergiesBuffer_Semaphore.release()  # Release lock after reading the stack

                        if response_data == []:
                            print("Empty data")
                            response_data = []

                        response_data = np.array(response_data).tolist()
                        response_json = json.dumps(response_data)
                        response_json  += "~"
                        conn.sendall(response_json.encode())

                elif data.decode().strip() == "GET /Parameters":

                        response_data = [GlobalParameters.MusclesNumber,GlobalParameters.synergiesNumber,GlobalParameters.sampleRate] #PM_DS.PM_DataStruct.circular_stack.get_vectors(3)

                        if response_data == []:
                            print("Empty data")
                            response_data = []

                        response_data = np.array(response_data).tolist()
                        response_json = json.dumps(response_data)
                        response_json  += "~"
                        conn.sendall(response_json.encode())
                #if data.decode().strip() == "DISCONNECT":
                    #Connected = False

                else:
                    #print("Invalid request")
                    pass
            except socket.timeout:
                print(f"Client {addr} timed out")
                break
    except (ConnectionResetError, ConnectionAbortedError) as e:
        print(f"Client {addr} connection lost: {e}")
    finally:
        conn.close()
        print(f"Connection with {addr} closed")


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Threads -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def Processing_Module_Client():
    notConnected = True
    while notConnected:
        try:
            client_socket.connect((HOST, PORT_Client))
            notConnected = False
        except Exception as e:
            #print(e)
            pass
    # Request Number of cahnnels from host

    GlobalParameters.MusclesNumber = Request("SensorsNumber")
    GlobalParameters.sampleRate = Request("SampleRate")
    try:
        GlobalParameters.Initialize()
    except Exception as e:
        print(e)
        return
    PM_DS.PM_DataStruct.InitializeRawDataBuffer()

    '''recieved = Request("StartDataStreaming")
    if recieved == "[1]":
        print("Data streaming started")'''
    # Loop to request data
    while True:
        #print("                           PM Client live")
        try:
            try:
                if GlobalParameters.RequestAngles == True:
                    data = Request("Angles")
                    #print("Angles")
                    angles = []
                    if data != []:
                        for element in data:
                            if element != '':
                                angles.append(int(element))
                        #msgbox.alert(text = "The angles are: " + str(angles), title = "Angles", button = "OK")
                        GlobalParameters.synergy_CursorMap = angles
                        GlobalParameters.AnglesRecieved = True
                        GlobalParameters.RequestAngles = False
                        GlobalParameters.CalibrationStage = 0
                        GlobalParameters.synergiesNumber = len(angles)
                        # msgbox.alert("lo hizo")
                        GlobalParameters.SynergyBase = GlobalParameters.modelsList[GlobalParameters.synergiesNumber-2][1]
                        # msgbox.alert("lo hizo 2")
                        GlobalParameters.SynergyBaseInverse = GlobalParameters.modelsList[GlobalParameters.synergiesNumber-2][2]
                        
                        
                        # print("Angles recieved", angles)
                        #msgbox.alert(text = str(GlobalParameters.SynergyBase), title = "Angles", button = "OK")

                    Request("data")

                else:
                    data = Request("data")
                    formated_data = Dictionary_to_matrix(data)
                    PM_DS.stack_lock.acquire()  # Acquire lock before accessing the stack
                    PM_DS.PM_DataStruct.circular_stack.add_matrix(formated_data)
                    PM_DS.stack_lock.release()  # Release lock after reading the stack

            except Exception as e:
                print("PM Client", e)
                msgbox.alert("Extra data")

        except socket.error as e:
            print("Connection error:", e)
            continue
            # Manage a connection error
        #time.sleep(0.001)


def Processing_Module_Server():
    server_socket.bind((HOST, PORT_Server))
    # Listen the inner connections:
    print("Server listening on", HOST, "port", PORT_Server)
    server_socket.listen(2)

    while True:
        try:
            # Accept the connection and open a thread to handle the client.
            conn, addr = server_socket.accept()
            thread = Thread(target = Handle_Client, args=(conn, addr))
            thread.start()
        except Exception as e:
            print(f"Error accepting connections: {e}")
            break
    #server_socket.close()

PM_Client_thread = Thread(target=Processing_Module_Client,daemon=True)
PM_Server_thread = Thread(target=Processing_Module_Server,daemon=True)
