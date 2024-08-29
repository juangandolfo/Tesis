import GlobalParameters
import PM_DataStructure as PM_DS
import socket
import json
import time
import msgpack as pack
import numpy as np
from threading import Thread
import LocalCircularBufferVector as Buffer
import pymsgbox as msgbox
from io import BytesIO
import threading
import pandas as pd

synergies_Lock = threading.Lock()

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
def Request(request):
    response_data = []
    try:
        client_socket.sendall(request.encode())
    except socket.error as e:
            print("PM request:", e)
    data = b''
    
    try:
        while True:
            chunk = client_socket.recv(1024)
            if b'END'in chunk:
                chunk = chunk[:-3]
                data += chunk
                #print("delimiter found")
                break
            elif b"TC" in chunk:
                GlobalParameters.TerminateCalibration = True
                chunk = chunk[:-2]
                data += chunk
                break
            elif b"CS1" in chunk:
                GlobalParameters.CalibrationStage = 1
                chunk = chunk[:-3]
                data += chunk
                break
            elif b"CS2" in chunk:
                GlobalParameters.CalibrationStage = 2
                chunk = chunk[:-3]
                data += chunk
                break
            elif b"CS3" in chunk:
                GlobalParameters.CalibrationStage = 3
                chunk = chunk[:-3]
                data += chunk
                break
            elif b"CS4" in chunk:
                GlobalParameters.CalibrationStage = 4
                chunk = chunk[:-3]
                data += chunk
                break
            elif b"CSF" in chunk:
                GlobalParameters.CalibrationStage = 0
                chunk = chunk[:-3]
                data += chunk
                break
            else: 
                data += chunk
                
    except socket.timeout as e:
        print("PM Client timeout", e)
    except socket.error as e:
        print("PM Client socket error", e)
    except Exception as e:
        msgbox.alert(e)
    
    try:
        if data == b'\x90': 
            raise Exception("PM:No data received")
        else:
            response_data = pack.unpackb(data, max_array_len = len(data), raw=False)
    except Exception as e:
        #msgbox.alert(e)
        pass
        
    return response_data

# Function to handle the connection with a client
def Handle_Client(conn,addr):
    print(f"Connected by {addr}")
    conn.settimeout(3)
    
    try:
        while True:
            time.sleep(0.025)
            print("                                                      PM Server live")
            try:
                data = conn.recv(1024)
                if not data:
                    # No data received, client has likely disconnected
                    print(f"Client {addr} disconnected")
                    continue

                # Check if the received data is a GET request for "/data"
                if  data.decode().strip() == "GET /data1":
                    PM_DS.PositionOutput_Semaphore.acquire()
                    response_data = np.trunc(PM_DS.PM_DataStruct.positionOutput)
                    PM_DS.PM_DataStruct.positionOutput = PM_DS.PM_DataStruct.positionOutput - response_data
                    PM_DS.PositionOutput_Semaphore.release()

                    if response_data == []:
                        response_data = [0,0]

                    response_data = np.asarray(response_data).tolist()
                    #print(response_data)
                    response_json = pack.packb(response_data, use_bin_type=True)  # Convert the dictionary to JSON and enconde into bytes
                    conn.sendall(response_json)
                    #print("PM: Data sent:", response_data)

                elif  data.decode().strip() == "GET /Muscles":
                    # with synergies_Lock:
                        #print("------------------------------------------------------GET /Muscles")
                        PM_DS.ProcessedDataBuffer_Semaphore.acquire()  # Acquire lock before accessing the stack
                        response_data = PM_DS.ProcessedDataBuffer.get_vectors(1)
                        PM_DS.ProcessedDataBuffer_Semaphore.release()  # Release lock after reading the stack
                        
                        if response_data == []:
                            #print("Empty data")
                            response_data = []
                        else:   
                            response_data = np.asarray(response_data).tolist()

                        #print(response_data)
                        try:
                            serialized_data = pack.packb(response_data,use_bin_type=True) 
                        except Exception as e:
                            msgbox.alert(f'Muscles pack {e}')
                        serialized_data  += b'END' # Add a delimiter at the end
                        if serialized_data[-3:] == b'END':
                            try:    
                                conn.sendall(serialized_data)
                            except Exception as e:
                                msgbox.alert("PM comms sending", e) 
                        else: 
                            msgbox.alert('fail')
                    #msgbox.alert(serialized_data)
                    # Convert the dictionary to JSON and enconde intio bytes
                    
                    #print("Data sent:", serialized_data)

                elif data.decode().strip() == "GET /Synergies":
                    # with synergies_Lock:
                        PM_DS.SynergiesBuffer_Semaphore.acquire()  # Acquire lock before accessing the stack
                        response_data = PM_DS.SynergiesBuffer.get_vectors(1) #PM_DS.PM_DataStruct.circular_stack.get_vectors(3)
                        PM_DS.SynergiesBuffer_Semaphore.release()  # Release lock after reading the stack

                        if response_data == []:
                            #print("Empty data")
                            response_data = []
                        else:   
                            response_data = np.asarray(response_data).tolist()
                        try:
                            serialized_data = pack.packb(response_data, use_bin_type=True) 
                        except Exception as e:  
                            msgbox.alert(f'Synergies pack {e}')
                        serialized_data  += b'END' # Add a delimiter at the end
                        # Convert the dictionary to JSON and enconde intio bytes
                        if serialized_data[-3:] == b'END':
                            conn.sendall(serialized_data)
                        else: 
                            msgbox.alert('fail')         

                elif data.decode().strip() == "GET /Parameters":
                        # response_data = [GlobalParameters.MusclesNumber,GlobalParameters.synergiesNumber,GlobalParameters.SubSamplingRate,GlobalParameters.SensorStickers] #PM_DS.PM_DataStruct.circular_stack.get_vectors(3)
                        # response_data = [GlobalParameters.MusclesNumber,GlobalParameters.synergiesNumber,GlobalParameters.SubSamplingRate] #PM_DS.PM_DataStruct.circular_stack.get_vectors(3)
                        response_data = {
                            'MusclesNumber': GlobalParameters.MusclesNumber,
                            'SynergiesNumber': GlobalParameters.synergiesNumber,
                            'SubSamplingRate': GlobalParameters.SubSamplingRate,
                            'SensorStickers': GlobalParameters.SensorStickers
                        }
                        if response_data == []:
                            #print("Empty data")
                            response_data = []
                        else:
                            response_data = np.array(response_data).tolist()
                        try:
                            serialized_data = pack.packb(response_data, use_bin_type=True) 
                        except Exception as e:  
                            msgbox.alert(e)
                        serialized_data  += b'END' # Add a delimiter at the end
                        conn.sendall(serialized_data)

                elif data.decode().strip() == "GET /Ping":
                    GlobalParameters.PingRequested = True
                    response_data = [1]
                    try:
                        serialized_data = pack.packb(response_data, use_bin_type=True) 
                    except Exception as e:  
                        msgbox.alert(e)
                    serialized_data  += b'END'

                    conn.sendall(serialized_data)

                elif data.decode().strip() == "GET /PingUpdate":
                    response_data = [GlobalParameters.PingResponse]
                    GlobalParameters.PingResponse = 0
                    try:
                        serialized_data = pack.packb(response_data, use_bin_type=True) 
                    except Exception as e:  
                        msgbox.alert(e)
                    serialized_data  += b'END'

                    conn.sendall(serialized_data)

                else:
                    #print("Invalid request")
                    pass
                
            except socket.timeout:
                print(f"Client {addr} timed out")
                break
            except Exception as e:  
                print(data)
            
    except (ConnectionResetError, ConnectionAbortedError) as e:
        print(f"Client {addr} connection lost: {e}")

    except Exception as e:
        msgbox.alert(f'PM Comms Server {e}')
    finally:
        conn.close()
        msgbox.alert(f"Connection with {addr} closed")
    


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Threads -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def Processing_Module_Client():
    try:
        notConnected = True
        while notConnected:
            try:
                client_socket.connect((HOST, PORT_Client))
                notConnected = False
            except Exception as e:
                #print(e)
                pass
        # Request Number of cahnnels from host
        GlobalParameters.MusclesNumber = Request("GET /SensorsNumber")
        GlobalParameters.SensorStickers = Request("GET /SensorStickers")
        GlobalParameters.sampleRate = Request("GET /SampleRate")
        GlobalParameters.Subsampling_NumberOfSamples = GlobalParameters.sampleRate/GlobalParameters.SubSamplingRate
        GlobalParameters.ExperimentTimestamp = Request("GET /ExperimentTimestamp")
        try:
            GlobalParameters.Initialize()
        except Exception as e:
            print(e)
            return
        PM_DS.PM_DataStruct.InitializeRawDataBuffer()

        RequestTimes = []
        counter3 = 0
        # Loop to request data
        while True:
            print("                           PM Client live")
            try:
                try:
                    if GlobalParameters.RequestAngles == True:
                        data = Request("GET /Angles")
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
                            GlobalParameters.SynergyBase = GlobalParameters.modelsList[GlobalParameters.synergiesNumber-2][1]
                            GlobalParameters.SynergyBaseInverse = GlobalParameters.modelsList[GlobalParameters.synergiesNumber-2][2]
                            
                            # print("Angles recieved", angles)
                            #msgbox.alert(text = str(GlobalParameters.SynergyBase), title = "Angles", button = "OK")
                    
                    elif GlobalParameters.RequestCalibrationTime == True:
                        try: 
                            response = Request("GET /CalibrationTime")
                        except Exception as e:
                            msgbox.alert(e)
                        GlobalParameters.TimeCalibStage3 = response
                        GlobalParameters.RequestCalibrationTime = False
                        
                    elif GlobalParameters.PlotThresholds == True:
                        try: 
                            response = Request("PLOT /Thresholds")
                        except Exception as e:
                            msgbox.alert(f'PMC: Thresholds {e}')
                        if response[0] == 1:
                            try:
                                serialized_data = pack.packb(GlobalParameters.Threshold.tolist(), use_bin_type=True) 
                                client_socket.sendall(serialized_data)
                            except Exception as e:
                                msgbox.alert(e)  
                            if response[0] == 1:
                                GlobalParameters.PlotThresholds = False
                    
                    elif GlobalParameters.PlotPeaks == True:
                        try: 
                            response = Request("PLOT /Peaks")
                        except Exception as e:
                            msgbox.alert(f'PMC: Peaks {e}')
                        if response[0] == 1:
                            try:
                                serialized_data = pack.packb(GlobalParameters.PeakActivation.tolist(), use_bin_type=True) 
                                client_socket.sendall(serialized_data)
                            except Exception as e:
                                msgbox.alert(e)  
                            if response[0] == 1:
                                GlobalParameters.PlotPeaks = False
                    
                    elif GlobalParameters.PlotSynergiesDetected == True:
                        try: 
                            response = Request("PLOT /Detection")
                        except Exception as e:
                            msgbox.alert(f'PMC: Detection {e}')
                        if response[0] == 1:
                            DetectionModels = {}
                            for i in range(len(GlobalParameters.modelsList)):
                                key = f'{i+2} Synergies'
                                value = GlobalParameters.modelsList[i][1].tolist()
                                DetectionModels[key] = value
                            DetectionModels['vafs'] = (np.asarray(GlobalParameters.vafs)*100).tolist()

                            try:
                                serialized_data = pack.packb(DetectionModels, use_bin_type=True) 
                                serialized_data  = serialized_data + b'END'
                                client_socket.sendall(serialized_data)
                            except Exception as e:
                                msgbox.alert(e)  
                            
                            if response[0] == 1:
                                GlobalParameters.PlotSynergiesDetected = False
                                GlobalParameters.AnglesRecieved = False
                                GlobalParameters.RequestAngles = True

                    elif GlobalParameters.UploadFromJson == True:
                        GlobalParameters.UploadFromJson = False
                        try: 
                            response = Request("UPLOAD /Configurations")
                        except Exception as e:
                            msgbox.alert(f'PMC: Configurations {e}')
                        if response[0] == 1:
                            configurationDictionary = Request("GET /JsonConfiguration")
                            GlobalParameters.Threshold = np.asarray(configurationDictionary['Thresholds'])
                            GlobalParameters.PeakActivation = np.asarray(configurationDictionary['Peaks'])
                            GlobalParameters.SynergyBase = np.asarray(configurationDictionary['SynergyBase'])
                            GlobalParameters.SensorStickers = configurationDictionary['SensorStickers']
                            synergy_CursorMap = np.asarray(configurationDictionary['synergy_CursorMap'])
                            angles = []
                            for element in synergy_CursorMap:
                                angles.append(int(element))
                            GlobalParameters.synergy_CursorMap = angles
                            GlobalParameters.synergiesNumber = len(angles)
                            GlobalParameters.JsonReceived = True
                    
                    elif GlobalParameters.PingRequested == True:
                        try: 
                            response = Request("GET /Ping")
                        except Exception as e:
                            msgbox.alert(f'PMC: Ping {e}')
                        if response[0] == 1:
                            GlobalParameters.PingResponse = 1
                            GlobalParameters.PingRequested = False

                    else:
                        try:
                            t1 = time.time()
                            data = Request("GET /data")
                            RequestTimes.append(time.time()-t1)
                            counter3 += 1
                            if counter3>3000:
                                try:
                                    frame = pd.DataFrame(RequestTimes).to_csv('./RequestTime.csv')
                                    # Save the DataFrame to a CSV file
                                    counter3 = 0
                                    RequestTimes = []
                                    msgbox.alert("guardo RT")
                                except Exception as e:
                                    msgbox.alert(e)
                            formated_data = np.asarray(data)
                            if GlobalParameters.DetectingSynergies == False:
                                PM_DS.stack_lock.acquire()  # Acquire lock before accessing the stack
                                PM_DS.PM_DataStruct.circular_stack.add_matrix(formated_data)
                                PM_DS.stack_lock.release()  # Release lock after reading the stack
                                time.sleep(0.025)            
                            else:
                                #print("Detecting synergies")
                                pass
                        except Exception as e:
                            msgbox.alert(f"PMC: Data {e}")
                            pass
                except Exception as e:
                    msgbox.alert(f"PM Client {e}")
                    #print(data)
            except socket.error as e:
                msgbox.alert(f"Connection error:{e}")
                continue
            except Exception as e:
                msgbox.alert(f"PM Client {e}")
                # Manage a connection error
            #time.sleep(0.001)
    except Exception as e:
        msgbox(e)


def Processing_Module_Server():
    server_socket.bind((HOST, PORT_Server))
    
    # Listen the inner connections:
    print("Server listening on", HOST, "port", PORT_Server)
    server_socket.listen(2)

    while True:
        try:
            # Accept the connection and open a thread to handle the client.
            conn, addr = server_socket.accept()
            conn.setblocking(False)
            thread = Thread(target = Handle_Client, args=(conn, addr))
            thread.start()
        except Exception as e:
            print(f"Error accepting connections: {e}")
            break
    
PM_Client_thread = Thread(target=Processing_Module_Client,daemon=True)
PM_Server_thread = Thread(target=Processing_Module_Server,daemon=True)
