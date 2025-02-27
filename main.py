from multiprocessing import Process
import time
import ProcessingModule.PM_Communications as PM_Comms
import ProcessingModule.PM_Processing as PM_Proc
import asyncio
from DataServer.UIControls.FrameController import *

def API_Server():
    app = QApplication(sys.argv)
    config_folder = 'ExperimentsFiles'
    controller = FrameController(config_folder)
    sys.exit(app.exec_())

def PM():
    PM_Comms.PM_Client_thread.start()
    PM_Comms.PM_Server_thread.start()
    PM_Proc.PM_Calibration.start()
    asyncio.run(PM_Comms.start_async_server())
    while True:
        time.sleep(0.001)
        pass

if __name__ == "__main__":
    API_Server_process = Process(target=API_Server)
    PM_process = Process(target=PM)

    API_Server_process.start()
    PM_process.start()

