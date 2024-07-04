"""
Controller class for the Data Collector GUI
This is the controller for the GUI that lets you connect to a base, scan via rf for sensors, and stream data from them in real time.
"""

from collections import deque
from threading import Thread
from Plotter.GenericPlot import *
from AeroPy.TrignoBase import *
from AeroPy.DataManager import *
import subprocess
import time
import sys
#from API_Server_Nuevo import *
from Aero_Nuevo import *
import SensorInformation
if API_Parameters.DelsysMode:
    import Delsys_API_Server as API_Server
else:
    import API_Server_Nuevo as API_Server

import API_Parameters
import pymsgbox as msgbox

clr.AddReference("System.Collections")
from System.Collections.Generic import List
from System import Int32

if API_Parameters.DelsysMode:
    base = TrignoBase()
    TrigBase = base.BaseInstance
else:
    TrigBase = AeroPyNuevo()

app.use_app('PySide2')

class PlottingManagement():
    def __init__(self):
        #self.EMGplot = EMGplot                      # Plot canvas for EMG data
        self.packetCount = 0                        # Number of packets received from base
        self.pauseFlag = False                      # Flag to start/stop collection and plotting
        self.numSamples = 10000                     # Default number of samples to visualize at a time
        self.DataHandler = DataKernel(TrigBase)     # Data handler for receiving data from base
        self.outData = [[0]]
        self.Index = None
        self.newTransform = None

        self.VisualizationProcess = 0
        self.CursorProcess = 0

    def streaming(self):
        """This is the data processing thread"""
        self.emg_queue = deque()
        while self.pauseFlag is False:
            self.DataHandler.processData(self.emg_plot)

    def vispyPlot(self):
        """Plot Thread"""
        skipCount = 0
        while self.pauseFlag is False:
            if len(self.emg_plot) >= 2:
                incData = self.emg_plot.popleft()       # Data at time T-1
                self.outData = list(np.asarray(incData, dtype='object')[tuple([self.dataStreamIdx])])
                if self.dataStreamIdx and self.outData[0].size > 0:
                    try:
                        self.EMGplot.plot_new_data(self.outData, [self.emg_plot[0][i][0] for i in self.dataStreamIdx])
                    except IndexError:
                        print("Index Error Occurred: CollectDataController.py - line 49")


    def threadManager(self):

        time.sleep(3)

        #if API_Parameters.DelsysMode:
        #    API_server_thread=Thread(target=API_Server.API_Server, args=(TrigBase,self.dataStreamIdx), daemon=True)
        #    API_server_thread.start()
        #else:
        API_server_thread=Thread(target=API_Server.API_Server, args=(TrigBase,self.dataStreamIdx), daemon=True)
        API_server_thread.start()




    #---------------------------------------------------------------------------------
    #---- Callback Functions
    def PipelineState_Callback(self):
        return TrigBase.GetPipelineState()

    def Connect_Callback(self):
        """Callback to connect to the base"""
        TrigBase.ValidateBase(key, license)

    def Pair_Callback(self):
        """Callback to tell the base to enter pair mode for new sensors"""
        if TrigBase.GetPipelineState() == 'Finished' or TrigBase.GetPipelineState() == 'Armed':
            self.Reset_Callback()
        TrigBase.PairSensor()

    def Scan_Callback(self):
        """Callback to tell the base to scan for any available sensors"""
        if TrigBase.GetPipelineState() == 'Finished' or TrigBase.GetPipelineState() == 'Armed':
            self.Reset_Callback()

        f = TrigBase.ScanSensors().Result
        self.nameList = TrigBase.GetSensorNames()
        
        self.ActiveSerialNumbers = []
        API_Parameters.SensorStickers = []
        for i in range(len(self.nameList)):
            self.ActiveSerialNumbers.append(str(self.nameList[i]).split(" ")[0])
        
        
        for SerialNumber in self.ActiveSerialNumbers:
            for sensor in SensorInformation.sensors:
                if SerialNumber == sensor["SerialNumber"]:
                    if len(sensor["Channels"]) > 1:
                        for channel in sensor["Channels"]:
                            channelName = sensor["Sticker"] + channel 
                            API_Parameters.SensorStickers.append(channelName)
                    else:
                        channelName = sensor["Sticker"] 
                        API_Parameters.SensorStickers.append(channelName)
                    
        print(API_Parameters.SensorStickers)

        self.SensorsFound = len(self.nameList)
        TrigBase.SelectAllSensors()
        return self.nameList

    def StartCalibration_Callback(self):
        """Callback to start the data stream from Sensors"""
        self.pauseFlag = False
        if TrigBase.GetPipelineState() == 'Connected':

            TrigBase.Configure()
            self.sampleRates = [[] for i in range(self.SensorsFound)]
            self.samplesPerFrame = [[] for i in range(self.SensorsFound)]

            # ---- Discover sensor channels
            self.dataStreamIdx = []  # This list indexes into the sensor data array, selecting relevant data to visualize
            plotCount = 0
            idxVal = 0
            for i in range(self.SensorsFound):
                selectedSensor = TrigBase.GetSensorObject(i)
                if len(selectedSensor.TrignoChannels) > 0:
                    for channel in range(len(selectedSensor.TrignoChannels)):
                        print(selectedSensor.TrignoChannels[channel].Name)
                        self.sampleRates[i].append((selectedSensor.TrignoChannels[channel].SampleRate,
                                                    selectedSensor.TrignoChannels[channel].Name))
                        self.samplesPerFrame[i].append(selectedSensor.TrignoChannels[channel].SamplesPerFrame)
                        # ---- Collect the EMG channels for visualization, excluding skin check channels
                        if "EMG" in selectedSensor.TrignoChannels[channel].Name:

                            if "TrignoAvanti" in str(selectedSensor) and "RMS 2" in selectedSensor.TrignoChannels[
                                channel].Name:  # Avanti skin check
                                pass
                            elif "AvantiDoubleMini" in str(selectedSensor) and "RMS 2" in selectedSensor.TrignoChannels[
                                channel].Name:  # Duo Mini skin check 1
                                pass
                            elif "AvantiDoubleMini" in str(selectedSensor) and "RMS 4" in selectedSensor.TrignoChannels[
                                channel].Name:  # Duo Mini skin check 2
                                pass
                            else:
                                self.dataStreamIdx.append(idxVal)
                                plotCount += 1

                        idxVal += 1
            print(self.dataStreamIdx)
            API_Parameters.ChannelsNumber = len(self.dataStreamIdx)
            API_Parameters.SampleRate = max(self.sampleRates, key=lambda x: x[0])[0][0]
            # ---- Create the plotting canvas and begin visualization
            #self.EMGplot.initiateCanvas(None, None, plotCount, 1, self.numSamples)

        TrigBase.Start()
        self.threadManager()

    def Start_Callback(self):
        print(1)

    def Stop_Callback(self):
        """Callback to stop the data stream"""
        TrigBase.Stop()
        self.pauseFlag = True
        print("Data Collection Complete")

    def Reset_Callback(self):
        TrigBase.ResetPipeline()

    def StartVisualization_Callback(self):
        try:
            if self.VisualizationProcess == 0:
                self.VisualizationProcess = subprocess.Popen('bokeh serve --show Visualizacion/streaming')
            else:
                self.VisualizationProcess.terminate()
                self.VisualizationProcess = 0
        except Exception as e:
            msgbox.alert(e)

    def StartCursor_Callback(self):
        try:
            if self.CursorProcess == 0:
                self.CursorProcess = subprocess.Popen(sys.executable + ' Cursor.py')
            else:
                self.CursorProcess.terminate()
                self.CursorProcess = 0
        except Exception as e:
            msgbox.alert(e)
        

    #---------------------------------------------------------------------------------
    #---- Helper Functions
    def getSampleModes(self,sensorIdx):
        """Gets the list of sample modes available for selected sensor"""
        sampleModes = TrigBase.AvailibleSensorModes(sensorIdx)
        return sampleModes

    def getCurMode(self):
        """Gets the current mode of the sensors"""
        curModes = TrigBase.GetAllSampleModes()
        return curModes

    def setSampleMode(self,curSensor,setMode):
        """Sets the sample mode for the selected sensor"""
        TrigBase.SetSampleMode(curSensor,setMode)

    def setSampleMode_allSensors(self,setMode):
        """Sets the same sample mode for all the sensors (it works for the same model)"""
        for i in range(self.SensorsFound):
            self.setSampleMode(i,setMode)

    def setSampleMode_hardcoded(self):
        """For different sensors models. It sets a hardcoded sample mode with the same frequency"""
        for i in range(self.SensorsFound):
            selectedSensor = TrigBase.GetSensorObject(i)
            if "TrignoAvanti" in str(selectedSensor):
                self.setSampleMode(i,"EMG raw (2148 Hz), skin check (74 Hz), +/-11mv, 10-850Hz")
                #self.setSampleMode(i,"EMG raw (4370 Hz), skin check (74 Hz), +/-11mv, 20-450Hz")
            elif "AvantiDoubleMini" in str(selectedSensor):
                self.setSampleMode(i, "EMG raw x2 (2148Hz), +/-11mv, 10-850Hz")
            print("AllSampleModes", TrigBase.GetAllSampleModes()[i])
