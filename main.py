from multiprocessing import Process
import time
import ProcessingModule.ThreadManager as PM
from DataServer.UIControls.FrameController import *

def API_Server():
    app = QApplication(sys.argv)
    config_folder = 'ExperimentsFiles'
    controller = FrameController(config_folder)
    sys.exit(app.exec_())

if __name__ == "__main__":
    API_Server_process = Process(target=API_Server)
    PM_process = Process(target=PM.main)

    API_Server_process.start()
    PM_process.start()

