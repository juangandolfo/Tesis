import numpy as np
import threading

ChannelsNumber = 0
DelsysMode = True
SampleRate = 0
TerminateCalibrationFlag = False

CalibrationStageInitialized = False
CalibrationStageFinished = False
CalibrationStage = 0

AnglesReady = 0
#Angles = [1,1]
AnglesOutput = []
AnglesOutputSemaphore = threading.Semaphore(1)


