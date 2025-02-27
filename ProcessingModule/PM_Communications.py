import ProcessingModule.PM_Parameters as params
import ProcessingModule.PM_DataStructure as PM_DS
import socket
import json
import time
import msgpack as pack
import numpy as np
from threading import Thread
import General.LocalCircularBufferVector as Buffer
import pymsgbox as msgbox
import threading
import os
import asyncio

class Attempt():

    def __init__(self):
        self.Id = 0
        self.Start = params.sampleCounter
        self.Stop = params.sampleCounter
        self.Result = ""
        self.File = "ExperimentsFiles/Experiment-" + params.ExperimentTimestamp + "/Events.json" 
        self.initializeExperimentFile()

    def convertToJson(self):
        attemptDictionary = {
            "Id": self.Id,
            "Start": self.Start,
            "Stop": self.Stop,
            "Result": self.Result,
        }
        return attemptDictionary
    
    def initializeExperimentFile(self):
        filename = self.File
        # Check if file exists to avoid overwriting
        if not os.path.exists(filename):
            experiment_data = []
            with open(filename, 'w') as file:
                json.dump(experiment_data, file, indent=4)
    
    def saveAttempt(self):
        # Check if file exists to avoid overwriting
        with open(self.File) as file:
            data = json.load(file)
            data.append(self.convertToJson())
            with open(self.File, 'w') as file:
                json.dump(data, file, indent=4) 
        self.incrementId() 

    def setStart(self):
        self.Start = params.sampleCounter 

    def setStop(self):
        self.Stop = params.sampleCounter

    def setResult(self, result):
        self.Result = result    
    
    def incrementId(self):
        self.Id += 1

synergies_Lock = threading.Lock()

HOST = "127.0.0.1"  # Standard adress (localhost)
PORT_Client = 6001  # Port to get data from the File API Server
PORT_Server = 6002 # The port used by the PM Server
PORT_Async = 6003 # The port used by the PM Server

clients = set()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)




# Auxiliar functions -------------------------------------------------------------------------------------------------------------------------------------------------------------
def getAnswer(message,attempt):

    if  message == "GET /data1":
        PM_DS.PositionOutput_Semaphore.acquire()
        response_data = np.trunc(PM_DS.PM_DataStruct.positionOutput)
        PM_DS.PM_DataStruct.positionOutput = PM_DS.PM_DataStruct.positionOutput - response_data
        PM_DS.PositionOutput_Semaphore.release()
        
        if response_data == []:
            response_data = f'SET Speed/{[0,0]}'

        response_data = np.asarray(response_data).tolist()
        return response_data

    elif message == "POST /startAttempt":
        #msgbox.alert("Attempt started")
        attempt.setStart()
        return "Ok"
    
    elif message == "POST /win":
        attempt.setStop()
        attempt.setResult("Win")
        attempt.saveAttempt()
        return "Ok"

    elif message == "POST /loss":
        attempt.setStop()
        attempt.setResult("Loss")
        attempt.saveAttempt()
        return "Ok"

    elif message == "POST /restartAttempt":
        attempt.setStop()
        attempt.setResult("Restarted")
        attempt.saveAttempt()
        return "Ok"

    elif message == "POST /exit":
        attempt.setStop()
        attempt.setResult("Exit")
        attempt.saveAttempt()
        return "Ok"

    elif message == "GET /Muscles":
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

            return response_data

    elif message == "GET /Synergies":
        # with synergies_Lock:
            PM_DS.SynergiesBuffer_Semaphore.acquire()  # Acquire lock before accessing the stack
            response_data = PM_DS.SynergiesBuffer.get_vectors(1) #PM_DS.PM_DataStruct.circular_stack.get_vectors(3)
            PM_DS.SynergiesBuffer_Semaphore.release()  # Release lock after reading the stack

            if response_data == []:
                #print("Empty data")
                response_data = []
            else:   
                response_data = np.asarray(response_data).tolist()
            return response_data        

    elif message == "GET /Parameters":
            response_data = {
                'MusclesNumber': params.MusclesNumber,
                'SynergiesNumber': params.synergiesNumber,
                'SubSamplingRate': params.SubSamplingRate,
                'SensorStickers': params.SensorStickers
            }
            if response_data == []:
                #print("Empty data")
                response_data = []
            else:
                response_data = np.array(response_data).tolist()
            return response_data

    elif message == "GET /Ping":
        params.PingRequested = True
        response_data = [1]
        return response_data

    elif message == "GET /PingUpdate":
        response_data = [params.PingResponse, params.PingTimeFromDataServer]
        params.PingResponse = 0
        return response_data

    else:
        #print("Invalid request")
        pass

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
                params.TerminateCalibration = True
                chunk = chunk[:-2]
                data += chunk
                break
            elif b"CS1" in chunk:
                params.CalibrationStage = 1
                chunk = chunk[:-3]
                data += chunk
                break
            elif b"CS2" in chunk:
                params.CalibrationStage = 2
                chunk = chunk[:-3]
                data += chunk
                break
            elif b"CS3" in chunk:
                params.CalibrationStage = 3
                chunk = chunk[:-3]
                data += chunk
                break
            elif b"CS4" in chunk:
                params.CalibrationStage = 4
                chunk = chunk[:-3]
                data += chunk
                break
            elif b"CS5" in chunk:
                params.CalibrationStage = 5
                chunk = chunk[:-3]
                data += chunk
                break
            elif b"CSF" in chunk:
                params.CalibrationStage = 0
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
    global attempt

    print(f"Connected by {addr}")
    conn.settimeout(600)
    attempt = Attempt()
    
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
                    print(f"---------------------------------------------------------------------{response_data}")
                    response_json = pack.packb(response_data, use_bin_type=True)  # Convert the dictionary to JSON and enconde into bytes
                    conn.sendall(response_json)
                    #print("PM: Data sent:", response_data)

                elif data.decode().strip() == "POST /startAttempt":
                    #msgbox.alert("Attempt started")
                    attempt.setStart()
                    serialized_data = pack.packb("Ok")
                    conn.sendall(serialized_data)
                
                elif data.decode().strip() == "POST /win":
                    attempt.setStop()
                    attempt.setResult("Win")
                    attempt.saveAttempt()
                    serialized_data = pack.packb("Ok")
                    conn.sendall(serialized_data)

                elif data.decode().strip() == "POST /loss":
                    attempt.setStop()
                    attempt.setResult("Loss")
                    attempt.saveAttempt()   
                    serialized_data = pack.packb("Ok")
                    conn.sendall(serialized_data)

                elif data.decode().strip() == "POST /restartAttempt":
                    attempt.setStop()
                    attempt.setResult("Restarted")
                    attempt.saveAttempt()
                    serialized_data = pack.packb("Ok")
                    conn.sendall(serialized_data)

                elif data.decode().strip() == "POST /exit":
                    attempt.setStop()
                    attempt.setResult("Exit")
                    attempt.saveAttempt()
                    serialized_data = pack.packb("Ok")
                    conn.sendall(serialized_data)

                elif data.decode().strip() == "GET /Muscles":
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
                        # response_data = [params.MusclesNumber,params.synergiesNumber,params.SubSamplingRate,params.SensorStickers] #PM_DS.PM_DataStruct.circular_stack.get_vectors(3)
                        # response_data = [params.MusclesNumber,params.synergiesNumber,params.SubSamplingRate] #PM_DS.PM_DataStruct.circular_stack.get_vectors(3)
                        response_data = {
                            'MusclesNumber': params.MusclesNumber,
                            'SynergiesNumber': params.synergiesNumber,
                            'SubSamplingRate': params.SubSamplingRate,
                            'SensorStickers': params.SensorStickers
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
                    params.PingRequested = True
                    response_data = [1]
                    try:
                        serialized_data = pack.packb(response_data, use_bin_type=True) 
                    except Exception as e:  
                        msgbox.alert(e)
                    serialized_data  += b'END'

                    conn.sendall(serialized_data)

                elif data.decode().strip() == "GET /PingUpdate":
                    response_data = [params.PingResponse, params.PingTimeFromDataServer]
                    params.PingResponse = 0
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
                msgbox.alert(f"Client {addr} timed out")
                break
            except Exception as e:  
                msgbox.alert(f"PM Server {e}")
            
    except (ConnectionResetError, ConnectionAbortedError) as e:
        print(f"Client {addr} connection lost: {e}")

    except Exception as e:
        msgbox.alert(f'PM Comms Server {e}')
    finally:
        conn.close()
        msgbox.alert(f"Connection with {addr} closed")

# Async Comms Server -------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
async def broadcast_messages():
    while True:
        await asyncio.sleep(0.5)  # Wait for 3 seconds
        message = f"Server broadcast"
        print(f"Broadcasting: {message}")

        for writer in clients.copy():
            try:
                writer.write(message.encode())
                await writer.drain()
            except Exception as e:
                print(f"Error sending to client: {e}")
                clients.discard(writer)

async def handle_async_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"New connection from {addr}")

    clients.add(writer)  # Register new client
    attempt = Attempt()

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            message = data.decode()
            Answer = getAnswer(message,attempt)
            
            writer.write(Answer.encode())

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        print(f"Connection closed from {addr}")
        clients.discard(writer)
        writer.close()
        await writer.wait_closed()

async def async_server():
    server = await asyncio.start_server(
        handle_async_client, 
        HOST, 
        PORT_Async
    )

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr} and port {addr[1]}')

    # Start broadcasting messages independently
    # asyncio.create_task(broadcast_messages())

    async with server:
        await server.serve_forever()




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
        params.MusclesNumber = Request("GET /SensorsNumber")
        params.SensorStickers = Request("GET /SensorStickers")
        params.sampleRate = Request("GET /SampleRate")
        params.Subsampling_NumberOfSamples = params.sampleRate/params.SubSamplingRate
        params.ExperimentTimestamp = Request("GET /ExperimentTimestamp")
        try:
            params.Initialize()
        except Exception as e:
            print(e)
            return
        PM_DS.PM_DataStruct.InitializeRawDataBuffer()

        #RequestTimes = []
        #counter3 = 0
        # Loop to request data
        while True:
            print("                           PM Client live")
            try:
                try:
                    if params.RequestAngles == True:
                        data = Request("GET /Angles")
                        angles = []
                        if data != []:
                            for element in data:
                                if element != '':
                                    angles.append(int(element))
                            #msgbox.alert(text = "The angles are: " + str(angles), title = "Angles", button = "OK")
                            params.synergy_CursorMap = angles
                            params.AnglesRecieved = True
                            params.RequestAngles = False
                            params.CalibrationStage = 0
                            params.synergiesNumber = len(angles)
                            params.SynergyBase = params.modelsList[params.synergiesNumber-2][1]
                            params.SynergyBaseInverse = params.modelsList[params.synergiesNumber-2][2]
                            
                            # print("Angles recieved", angles)
                            #msgbox.alert(text = str(params.SynergyBase), title = "Angles", button = "OK")
                    
                    elif params.RequestCalibrationTime == True:
                        try: 
                            response = Request("GET /CalibrationTime")
                        except Exception as e:
                            msgbox.alert(e)
                        params.TimeCalibStage3 = response
                        params.RequestCalibrationTime = False
                        
                    elif params.PlotThresholds == True:
                        try: 
                            response = Request("PLOT /Thresholds")
                        except Exception as e:
                            msgbox.alert(f'PMC: Thresholds {e}')
                        if response[0] == 1:
                            try:
                                serialized_data = pack.packb(params.Threshold.tolist(), use_bin_type=True) 
                                client_socket.sendall(serialized_data)
                            except Exception as e:
                                msgbox.alert(e)  
                            if response[0] == 1:
                                params.PlotThresholds = False
                    
                    elif params.PlotPeaks == True:
                        try: 
                            response = Request("PLOT /Peaks")
                        except Exception as e:
                            msgbox.alert(f'PMC: Peaks {e}')
                        if response[0] == 1:
                            try:
                                serialized_data = pack.packb(params.PeakActivation.tolist(), use_bin_type=True) 
                                client_socket.sendall(serialized_data)
                            except Exception as e:
                                msgbox.alert(e)  
                            if response[0] == 1:
                                params.PlotPeaks = False
                    
                    elif params.PlotSynergiesDetected == True:
                        try: 
                            response = Request("PLOT /Detection")
                        except Exception as e:
                            msgbox.alert(f'PMC: Detection {e}')
                        if response[0] == 1:
                            DetectionModels = {}
                            for i in range(len(params.modelsList)):
                                key = f'{i+2} Synergies'
                                value = params.modelsList[i][1].tolist()
                                DetectionModels[key] = value
                            DetectionModels['vafs'] = (np.asarray(params.vafs)*100).tolist()

                            try:
                                serialized_data = pack.packb(DetectionModels, use_bin_type=True) 
                                serialized_data  = serialized_data + b'END'
                                client_socket.sendall(serialized_data)
                            except Exception as e:
                                msgbox.alert(e)  
                            
                            if response[0] == 1:
                                params.PlotSynergiesDetected = False
                                params.AnglesRecieved = False
                                params.RequestAngles = True

                    elif params.UploadFromJson == True:
                        params.UploadFromJson = False
                        try: 
                            response = Request("UPLOAD /Configurations")
                        except Exception as e:
                            msgbox.alert(f'PMC: Configurations {e}')
                        if response[0] == 1:
                            configurationDictionary = Request("GET /JsonConfiguration")
                            params.Threshold = np.asarray(configurationDictionary['Thresholds'])
                            params.PeakActivation = np.asarray(configurationDictionary['Peaks'])
                            params.SynergyBase = np.asarray(configurationDictionary['SynergyBase'])
                            params.SensorStickers = configurationDictionary['SensorStickers']
                            synergy_CursorMap = np.asarray(configurationDictionary['synergy_CursorMap'])
                            angles = []
                            for element in synergy_CursorMap:
                                angles.append(int(element))
                            params.synergy_CursorMap = angles
                            params.synergiesNumber = len(angles)
                            params.JsonReceived = True
                    
                    elif params.UploadSimulationConfig == True:
                        params.UploadSimulationConfig = False
                        try: 
                            configurationDictionary = Request("GET /JsonConfiguration")
                        except Exception as e:
                            msgbox.alert(f'PMC: Simulation Configuration {e}')
                        params.Threshold = np.asarray(configurationDictionary['Thresholds'])
                        params.PeakActivation = np.asarray(configurationDictionary['Peaks'])
                        params.SynergyBase = np.asarray(configurationDictionary['SynergyBase'])
                        params.SensorStickers = configurationDictionary['SensorStickers']
                        synergy_CursorMap = np.asarray(configurationDictionary['synergy_CursorMap'])
                        angles = []
                        for element in synergy_CursorMap:
                            angles.append(int(element))
                        params.synergy_CursorMap = angles
                        params.synergiesNumber = len(angles)
                        params.SynergyBaseInverse = np.linalg.pinv(params.SynergyBase)
                        params.TerminateCalibration = True
                    
                    elif params.PingRequested == True:
                        try: 
                            response = Request("GET /Ping")
                        except Exception as e:
                            msgbox.alert(f'PMC: Ping {e}')
                        if response[0] == 1:
                            params.PingResponse = 1
                            params.PingTimeFromDataServer = response[1]
                            params.PingRequested = False

                    else:
                        try:
                            t1 = time.time()
                            data = Request("GET /data")
                            #RequestTimes.append(time.time()-t1)
                            # counter3 += 1
                            # if counter3>3000:
                            #     try:
                            #         frame = pd.DataFrame(RequestTimes).to_csv('./RequestTime.csv')
                            #         # Save the DataFrame to a CSV file
                            #         counter3 = 0
                            #         RequestTimes = []
                            #     except Exception as e:
                            #         msgbox.alert(e)
                            formated_data = np.asarray(data)
                            if params.DetectingSynergies == False:
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
        msgbox.alert(e)

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

async def start_async_server():
    try:
        # Uncomment the one you want to run:
        await async_server()
        # await async_client()
    except KeyboardInterrupt:
        print("Shutting down...")
