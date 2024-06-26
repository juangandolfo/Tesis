import numpy as np
import threading
from PySide2.QtCore import *
from PySide2.QtCore import QObject, Signal
import json
import time

ChannelsNumber = 0
DelsysMode = True
SampleRate = 0
TerminateCalibrationFlag = False

CalibrationStageInitialized = False
CalibrationStageFinished = False
CalibrationStage = 0

AnglesReady = 0
AnglesOutput = []
AnglesOutputSemaphore = threading.Semaphore(1)

Thresholds = [0,0]
Peaks = [0,0]
SynergiesModels = []
SynergiesNumber = 2
SynergyBase = []

PlotThresholds = False
PlotPeaks = False
PlotModels = False
PlotAngles = False

remaining_time = 5

ExperimentTimestamp = ''

class PlotSignal(QObject):
    signal = Signal()  # Define the signal attribute

PlotCalibrationSignal = PlotSignal()

def TwoDigitString(number):
    if number < 10:
        return "0" + str(number)
    else:
        return str(number)

def CreateExperimentName():
    global ExperimentTimestamp
    t = time.gmtime()
    ExperimentTimestamp = str(t.tm_year) + TwoDigitString(t.tm_mon) + TwoDigitString(t.tm_mday) + "-" + TwoDigitString(t.tm_hour) + TwoDigitString(t.tm_min) + TwoDigitString(t.tm_sec)

def UploadCalibrationFromJson():
    # Load the configuration from a JSON file
    with open('Configuration.json') as file:
        data = json.load(file)
        if ChannelsNumber != data['MusclesNumber']:
            raise Exception("The number of channels in the configuration file is different from the current configuration")
        else:
            Thresholds = data['Thresholds']
            Peaks = data['Peaks']
            AnglesOutput = data['Angles']
            SynergiesModels= data['SynergyBase']
    return Thresholds, Peaks, AnglesOutput, SynergiesModels
        
def SaveCalibrationToJson(ChannelsNumber,Thresholds, Peaks, AnglesOutput, SynergyBase):
    global ExperimentTimestamp
    data = {
            'MusclesNumber': ChannelsNumber,
            'Thresholds': np.asarray(Thresholds).tolist(),
            'Peaks': np.asarray(Peaks).tolist() ,
            'Angles': np.asarray(AnglesOutput).tolist(),
            'SynergyBase': np.asarray(SynergyBase).tolist()
            }
    json_array = json.dumps(data, sort_keys=True, indent=4)
    f = open('Configuration.json', 'w')
    f.write(json_array) 
    f.close()

    f = open('Calibrations\Calibration-' + ExperimentTimestamp + '.json', 'w')
    f.write(json_array)
    f.close()