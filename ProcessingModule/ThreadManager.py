import ProcessingModule.PM_Communications as PM_Comms
import ProcessingModule.PM_Processing as PM_Proc
import ProcessingModule.PM_Parameters as params

from threading import Thread
import time




def main():
    ServerThread = Thread(target=PM_Comms.Processing_Module_Server,daemon=True)
    ClientThread = Thread(target=PM_Comms.Processing_Module_Client,daemon=True)
    CalibrationThread = Thread(target=PM_Proc.CalibrationProcessing,daemon=True)
    ProcessingThread = Thread(target=PM_Proc.Processing,daemon=True)
    while True:
        if not ClientThread.is_alive():
            ClientThread = Thread(target=PM_Comms.Processing_Module_Client,daemon=True)
            ClientThread.start()
        
        if not ServerThread.is_alive():
            ServerThread = Thread(target=PM_Comms.Processing_Module_Server,daemon=True)
            ServerThread.start()

        if params.InitializeCalibrationRequest:
            # Resets the flag
            params.InitializeCalibrationRequest = False
            params.TerminateCalibration = False
            
            # Kills the Processing thread if alive as it cant be running during calibration
            if ProcessingThread.is_alive():
                params.Processing = False
                ProcessingThread.join()
            
            # Initializes the calibration thread
            if not CalibrationThread.is_alive():
                CalibrationThread = Thread(target=PM_Proc.CalibrationProcessing,daemon=True)
                CalibrationThread.start()
            

        if params.Processing:
            if not ProcessingThread.is_alive():
                ProcessingThread = Thread(target=PM_Proc.Processing,daemon=True)
                ProcessingThread.start()

        time.sleep(0.001)
        