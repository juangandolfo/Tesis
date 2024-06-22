import socket
import random
import json
import time
import msgpack as pack
import numpy as np
import clr
import pymsgbox as msgbox
import matplotlib.pyplot as plt
clr.AddReference("System")
from System import Guid
import API_Parameters

HOST = "127.0.0.1"  # Standard adress (localhost)
PORT = 6001  # Port to listen on (non-privileged ports are > 1023)


def FormattedDictionary_to_PythonDictionary(formatted_dictionary, emgPositionVector):
    python_dictionary = {}
    #outArr = [[] for i in range(len(formatted_dictionary.Keys))] # matrix
    keys = []
    
    for i in formatted_dictionary.Keys:
        keys.append(i)
        
    '''for j in range(len(keys)):
        # outArr[j].append(np.asarray(formatted_dictionary[keys[j]], dtype='object'))
        # full data
    '''
    DataRows = min(set([len(formatted_dictionary[keys[i]]) for i in emgPositionVector]))
    # set(len(row) for row in keys)
    DataColumns = len(emgPositionVector)
    # DataRows = len(formatted_dictionary[keys[0]])
    OutMatrix = np.zeros((DataRows,DataColumns))
    for j in range(len(emgPositionVector)):
        # outArr[j].append(np.asarray(formatted_dictionary[keys[j]], dtype='object')) # matrix
        # python_dictionary[str(keys[j])] = np.asarray(formatted_dictionary[keys[j]]).tolist()
        OutMatrix[:,j] = np.asarray(formatted_dictionary[keys[emgPositionVector[j]]])[:DataRows]
        # python_dictionary[str(keys[emgPositionVector[j]])] = np.asarray(OutMatrix[j]).tolist()
    
    return OutMatrix.tolist()

def UploadCalibrationFromJson():
    # Load the configuration from a JSON file
    with open('Configuration.json') as f:
        data = json.load(f)
        #msgbox.alert(data["Angles"])
        print(data["Angles"])

def API_Server(AeroInstance,emgPositionVector):
    # Create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # Link the socket to the IP and PORT selected:
        s.bind((HOST, PORT))

        # Listen the inner connections:
        print("Delsys API Server listening on", HOST, "port", PORT)
        s.listen()

        # Accept the connection and open a socket to receive and send data.
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            BaseStarted = False
            while True:
                #print("                                                 API Server live")
                try:
                    s.settimeout(5)
                    DataReceived = conn.recv(1024)
                except Exception as e:
                    print("API", e)
                # Check if the received data is a GET request for "/data"
                data = DataReceived.decode().strip()
                print(data)
                if data == "GET /StartDataStreaming":
                    serialized_data = json.dumps(1) # Serialize the object using json
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                        #print(serialized_data)
                    except Exception as e:
                        print(e)
                elif data == "GET /data":
                    #print("Data requested")
                    dataReady = AeroInstance.CheckDataQueue()
                    if dataReady:
                        try:
                            response_data = FormattedDictionary_to_PythonDictionary(AeroInstance.PollData(),emgPositionVector)
                            #print(response_data)
                        except Exception as e:
                            msgbox.alert(e)
                    else:
                        response_data=[]

                    serialized_data = pack.packb(response_data,use_bin_type=True) # Serialize the object using json
                    if API_Parameters.TerminateCalibrationFlag:
                        serialized_data  += "TC" # Add a delimiter at the end
                        API_Parameters.TerminateCalibrationFlag = False

                    elif API_Parameters.CalibrationStageInitialized:
                            API_Parameters.CalibrationStageInitialized = False
                            # if not BaseStarted:
                            #     AeroInstance.Start()
                            #     BaseStarted = True
                            # else:
                            #     pass
                            if API_Parameters.CalibrationStage == 1:
                                serialized_data  += "CS1" # Add a delimiter at the end
                            elif API_Parameters.CalibrationStage == 2:
                                serialized_data  += "CS2" # Add a delimiter at the end
                            elif API_Parameters.CalibrationStage == 3:
                                serialized_data  += "CS3" # Add a delimiter at the end
                            elif API_Parameters.CalibrationStage == 4:
                                serialized_data  += "CS4" # Add a delimiter at the end
                    elif API_Parameters.CalibrationStageFinished:
                        API_Parameters.CalibrationStageFinished = False
                        serialized_data  += "CSF" # Add a delimiter at the end
                        #AeroInstance.Stop()
                        #BaseStarted = False
                    else:
                        serialized_data  += pack.packb(':') # Add a delimiter at the end
                    try:
                        conn.sendall(serialized_data)
                        #print("data sent:", serialized_data)
                    except Exception as e:
                        print("API sending", e)


                elif data == "GET /SensorsNumber":
                    print("Sensors number requested")
                    serialized_data = json.dumps(API_Parameters.ChannelsNumber)
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                        #print(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /SampleRate":
                    print("Sample rate requested")
                    serialized_data = json.dumps(API_Parameters.SampleRate)
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                    except Exception as e:
                        print(e)

                elif data == "GET /Angles":
                    API_Parameters.AnglesOutputSemaphore.acquire()
                    serialized_data = json.dumps(API_Parameters.AnglesOutput)
                    print(serialized_data)
                    API_Parameters.AnglesOutputSemaphore.release()
                    #msgbox.alert(text = "The angles are: " + serialized_data, title = "Angles", button = "OK")
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                    except Exception as e:
                        print(e)
                    dataReady = AeroInstance.CheckDataQueue()
                    if dataReady:
                        AeroInstance.PollData()
                
                elif data == "PLOT /Thresholds":
                    serialized_data = json.dumps([1])
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                    except Exception as e:
                        print(e)
                    
                    DataReceived = conn.recv(1024)
                    API_Parameters.Thresholds = np.array(json.loads(DataReceived.decode().strip()))
                    API_Parameters.PlotThresholds = True
                    try:
                        API_Parameters.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(e)
                    serialized_data = json.dumps([1])
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                    except Exception as e:
                        print(e)

                elif data == "PLOT /Peaks":
                    serialized_data = json.dumps([1])
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                    except Exception as e:
                        print(e)
                    
                    DataReceived = conn.recv(1024)
                    API_Parameters.Peaks = np.array(json.loads(DataReceived.decode().strip()))
                    API_Parameters.PlotPeaks = True
                    try:
                        API_Parameters.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(e)
                    serialized_data = json.dumps([1])
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                    except Exception as e:
                        print(e)

                elif data == "PLOT /Detection":
                    #msgbox.alert("Ploting Synergies")
                    serialized_data = json.dumps([1])
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                    except Exception as e:
                        print(e)
                    data = b''
                    while True:
                        try:
                            chunk = conn.recv(1024)
                            data += chunk
                            if b"~" in data:
                                serialized_data = data.decode().rstrip("~")
                                break
                        except Exception as e:
                            print(e)
                            break
                    
                    API_Parameters.SynergiesModels = json.loads(serialized_data)
                    API_Parameters.PlotModels = True
                    try:
                        API_Parameters.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(e)
                    serialized_data = json.dumps([1])
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                    except Exception as e:
                        print(e)                   
                
                elif data == "UPLOAD /Configurations":
                    UploadCalibrationFromJson()
                    serialized_data = json.dumps([1])
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                    except Exception as e:
                        print(e)
                    API_Parameters.CalibrationStageFinished = True

                    

                else:
                   print("Invalid request", data)
                   pass
