from DataServer.DataCollector.CollectDataWindow import CollectDataWindow, SimulationWindow
from DataServer.StartMenu.StartWindow import StartWindow
import sys
from PySide2.QtWidgets import *

class FrameController():
    def __init__(self, config_folder):
        self.config_folder = config_folder
        self.startWindow = StartWindow(self)
        self.collectWindow = CollectDataWindow(self)
        self.simulationWindow = SimulationWindow(self, config_folder)
        self.startWindow.show()

        self.curHeight = 650
        self.curWidth = 1115

    def showStartMenu(self):
        self.collectWindow.close()
        self.simulationWindow.close()
        self.startWindow.show()

    def showCollectData(self):
        self.startWindow.close()
        self.simulationWindow.close()
        self.collectWindow.show()

    def showSimulation(self):
        self.startWindow.close()
        self.collectWindow.close()
        self.simulationWindow.show()



def main():
    app = QApplication(sys.argv)
    config_folder = 'ExperimentsFiles'
    controller = FrameController(config_folder)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()




