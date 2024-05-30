from multiprocessing import Process
import subprocess
import socket
import time
import PM_Communications
import PM_Processing
import Cursor_Nuevo
from UIControls.FrameController import *
from threading import Thread


def API_Server():
    app = QApplication(sys.argv)
    controller = FrameController()
    sys.exit(app.exec_())


def PM():
    PM_Communications.PM_Client_thread.start()
    PM_Communications.PM_Server_thread.start()
    PM_Processing.PM_Calibration.start()
    while True:
        time.sleep(0.001)
        pass


if __name__ == "__main__":

    API_Server_process = Process(target=API_Server)
    PM_process = Process(target=PM)

    API_Server_process.start()
    PM_process.start()
