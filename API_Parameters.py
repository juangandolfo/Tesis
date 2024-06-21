import numpy as np
import threading
from PySide2.QtCore import *
from PySide2.QtCore import QObject, Signal

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

PlotThresholds = False
PlotPeaks = False
PlotModels = False
PlotAngles = False

remaining_time = 15

class PlotSignal(QObject):
    signal = Signal()  # Define the signal attribute

PlotCalibrationSignal = PlotSignal()