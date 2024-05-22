import PM_Communications
import PM_Processing
import GlobalParameters
import threading
import time

PM_Communications.server_socket.bind((PM_Communications.HOST, PM_Communications.PORT_Server))

serverThread = threading.Thread(target=PM_Communications.Processing_Module_Server,daemon=True)
clientThread = threading.Thread(target=PM_Communications.Processing_Module_Client,daemon=True)
calibrationThread = threading.Thread(target=PM_Processing.CalibrationProcessing,daemon=True)
processingThread = threading.Thread(target=PM_Processing.Processing,daemon=True)



serverThread.start()
time.sleep(0.2)
clientThread.start()
time.sleep(0.2)
#processingThread.start()
calibrationThread.start()
while True:
    if GlobalParameters.TerminateCalibration == True:
        #calibrationThread.stop()
        time.sleep(0.2)
        processingThread.start()
        break
        
