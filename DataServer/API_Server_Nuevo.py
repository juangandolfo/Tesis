import socket
import random
import json
import time
import pickle
from DataServer.Aero_Nuevo import *
import msgpack as pack
import numpy as np
import pymsgbox as msgbox


HOST = "127.0.0.1"  # Standard adress (localhost)
PORT = 6001  # Port to listen on (non-privileged ports are > 1023)

def DictionaryToMatrix(formatted_dictionary, emgPositionVector):
    '''python_dictionary = {}
    for key in formatted_dictionary.Keys:
        try:
            python_dictionary[key] = formatted_dictionary[key]
        except Exception as e:
            msgbox.alert(f"FormattedDictionary_to_PythonDictionary {e}")
    return python_dictionary'''
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
    DataColumns = len(emgPositionVector)
    OutMatrix = np.zeros((DataRows,DataColumns))
    for j in range(len(emgPositionVector)):
        OutMatrix[:,j] = np.asarray(formatted_dictionary[keys[emgPositionVector[j]]])[:DataRows]
    return OutMatrix.tolist()

def API_Server(AeroInstance, emgPositionVector):
    # Create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # Link the socket to the IP and PORT selected: 
        s.bind((HOST, PORT))

        # Listen the inner connections:
        print("API Server listening on", HOST, "port", PORT)
        s.listen()
        
        # Accept the connection and open a socket to receive and send data. 
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                #print("                                                 API Server live")
                try:
                    s.settimeout(5)
                    DataReceived = conn.recv(1024)
                except Exception as e:
                    print("API", e)
                # Check if the received data is a GET request for "/data"
                data = DataReceived.decode().strip()
                
                # Check if the received data is a GET request for "/data"
                if data == "GET /data":
                    dataReady = AeroInstance.CheckDataQueue()
                    if dataReady:
                        try:
                            result = AeroInstance.PollData()
                            response_data = DictionaryToMatrix(result,emgPositionVector)
                        except Exception as e:
                            msgbox.alert(e)
                            # msgbox.alert(f'{data} {e} {result} {emgPositionVector}')
                    else:
                        response_data=[]
                    
                    serialized_data = pack.packb(response_data,use_bin_type=True) # Serialize the object using msgpack

                    if params.TerminateCalibrationFlag:
                        serialized_data  += b"TC" # Add a delimiter at the end
                        params.TerminateCalibrationFlag = False

                    elif params.CalibrationStageInitialized:
                        params.CalibrationStageInitialized = False

                        if params.CalibrationStage == 1:
                            serialized_data  += b"CS1" # Add a delimiter at the end
                        elif params.CalibrationStage == 2:
                            serialized_data  += b"CS2" # Add a delimiter at the end
                        elif params.CalibrationStage == 3:
                            serialized_data  += b"CS3" # Add a delimiter at the end
                        elif params.CalibrationStage == 4:
                            serialized_data  += b"CS4" # Add a delimiter at the end

                    elif params.CalibrationStageFinished:
                        params.CalibrationStageFinished = False
                        serialized_data  += b"CSF" # Add a delimiter at the end

                    elif params.SimulationCalibration == True:
                        params.SimulationCalibration = False
                        serialized_data  += b"CS5" # Add a delimiter at the end
                        
                    else:
                        serialized_data += b'END' # Add a delimiter at the end
                        #print(serialized_data)
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print("API sending", e)

                elif data == "GET /SensorsNumber":
                    serialized_data = pack.packb(params.ChannelsNumber, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /SensorStickers":
                    params.SensorStickers = ['M1', 'M2', 'M3']
                    serialized_data = pack.packb(params.SensorStickers, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /SampleRate":
                    serialized_data = pack.packb(params.SampleRate, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /Angles":
                    params.AnglesOutputSemaphore.acquire()
                    serialized_data = pack.packb(params.AnglesOutput, use_bin_type=True)
                    params.AnglesOutputSemaphore.release()
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)
                    dataReady = AeroInstance.CheckDataQueue()
                    if dataReady:
                        AeroInstance.PollData()              
                
                elif data == "PLOT /Thresholds":
                    try:
                        serialized_data = pack.packb([1], use_bin_type=True)
                    except Exception as e:
                        msgbox.alert(f'{data} {e}')
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)
                    
                    data = conn.recv(1024)
                    params.Thresholds = np.array(pack.unpackb(data.strip(), raw=False))
                    msgbox.alert(f"thresholds API: {params.Thresholds}")
                    params.PlotThresholds = True
                    try:
                        params.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(f'{data} {e}')
                    serialized_data = pack.packb([1], use_bin_type=True)
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "PLOT /Peaks":
                    serialized_data = pack.packb([1], use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)
                    
                    DataReceived = conn.recv(1024)
                    params.Peaks = np.array(pack.unpackb(DataReceived.strip(),  raw=False))
                    params.PlotPeaks = True
                    try:
                        params.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(f'{data} {e}')
                    serialized_data = pack.packb([1], use_bin_type=True)
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "PLOT /Detection":
                    serialized_data = pack.packb([1], use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)
                    data = b''
                    while True:
                        try:
                            chunk = conn.recv(1024)
                            if b'END' in chunk:
                                chunk = chunk[:-3]
                                data += chunk
                                break
                            else:
                                data += chunk
                        except Exception as e:
                            msgbox.alert(f'{data} {e}')
                            break
                    try:
                        params.SynergiesModels = pack.unpackb(data, max_array_len = len(data), raw=False)
                    except Exception as e:
                        msgbox.alert(f'{data} {e}')
                    params.PlotModels = True
                    try:
                        params.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(f'{data} {e}')
                    serialized_data = pack.packb([1], use_bin_type=True)
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)                   
                
                elif data == "UPLOAD /Configurations":
                    try:
                        Thresholds, Peaks, AnglesOutput, SynergyBase, SensorStickers = params.UploadCalibrationFromJson()
                        params.Thresholds = Thresholds
                        params.Peaks = Peaks
                        params.AnglesOutput = AnglesOutput
                        params.SynergyBase = SynergyBase
                        params.SensorStickers = SensorStickers
                        params.SynergiesNumber = len(AnglesOutput)
                    except Exception as e:
                        msgbox.alert(e)                    
                    
                    serialized_data = pack.packb([1], use_bin_type = True)
                    serialized_data  += b'END'
                    
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        msgbox.alert(e)
                    
                    params.PlotUploadedConfig = True
                    params.PlotCalibrationSignal.signal.emit()
                    params.CalibrationStageFinished = True

                elif data == "GET /JsonConfiguration":
                    dictionary = {"Thresholds": params.Thresholds,
                                  "Peaks": params.Peaks,
                                   "synergy_CursorMap": params.AnglesOutput,
                                   "SynergyBase": params.SynergyBase,
                                   "SensorStickers": params.SensorStickers}
                    serialized_data = pack.packb(dictionary, use_bin_type = True)  
                    serialized_data  += b'END' 
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        msgbox.alert(e)

                elif data == "GET /ExperimentTimestamp":
                    serialized_data = pack.packb(params.ExperimentTimestamp, use_bin_type = True)
                    serialized_data  += b'END' 
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        msgbox.alert(f'{data} {e}') 
                
                elif data == "GET /CalibrationTime":
                    serialized_data = pack.packb(params.TimeCalibStage3, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                else:
                   print("Invalid request", data)
                   
                    





