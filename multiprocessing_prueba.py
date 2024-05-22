from multiprocessing import Process
from threading import Thread
import PM_Communications 
import PM_Processing
import Cursor_Nuevo
import GlobalParameters
import time
import subprocess


def API():
    subprocess.run(['python', 'DelsysPythonDemo.py'])

def PM():
    PM_Client_thread = Thread(target=PM_Communications.Processing_Module_Client,daemon=True)
    PM_Server_thread = Thread(target=PM_Communications.Processing_Module_Server,daemon=True)
    PM_Calibration = Thread(target=PM_Processing.CalibrationProcessing,daemon=True)
    PM_Processing = Thread(target=PM_Processing.Processing,daemon=True)

    PM_Client_thread.start()
    time.sleep(0.01)
    PM_Server_thread.start()
    time.sleep(0.01)
    PM_Calibration.start()

    if GlobalParameters.TerminateCalibration == True:
        PM_Processing.start()

def Cursor():
    Cursor_thread=Thread(target=Cursor_Nuevo.Cursor,daemon=True)
    Cursor_thread.start()



if __name__ == '__main__':
    
    process1 = Process(target=API)
    process2 = Process(target=PM)
    process3 = Process(target=Cursor)

    process1.start()
    process2.start()
    if GlobalParameters.TerminateCalibration == True:
        process3.start()
   
   
    
   







    
    
    
    