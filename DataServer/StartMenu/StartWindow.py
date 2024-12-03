import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class StartWindow(QWidget):
    def __init__(self,controller):
        QWidget.__init__(self)
        self.controller = controller
        grid = QGridLayout()
        self.setStyleSheet("background-color:#DDDDDD;")  # Even Darker Light Steel Blue
        self.setWindowTitle("Start Menu")

        imageBox = QHBoxLayout()
        self.im = QPixmap("./Images/LogoUCU.png")
        self.label = QLabel()
        self.label.setPixmap(self.im)
        imageBox.addWidget(self.label)
        imageBox.setAlignment(Qt.AlignVCenter)
        grid.addLayout(imageBox,0,0)

        buttonBox=QHBoxLayout()
        buttonBox.setSpacing(20)

        button = QPushButton('Start Experiment', self)
        button.setToolTip('Start Experiment')
        button.objectName = 'Start Experiment'
        button.clicked.connect(self.Collect_Data_Callback)
        button.setFixedSize(200,100)
        button.setStyleSheet('QPushButton {color: #000066;}')
        buttonBox.addWidget(button)

        button2 = QPushButton('Start Simulation', self)
        button2.setToolTip('Start Simulation')
        button2.objectName = 'Start Simulation'
        button2.clicked.connect(self.Simulation_Callback)
        button2.setFixedSize(200,100)
        button2.setStyleSheet('QPushButton {color: #000066;}')
        buttonBox.addWidget(button2)

        grid.addLayout(buttonBox,1,0)

        self.setLayout(grid)
        self.setFixedSize(self.width(),self.height())

    def Collect_Data_Callback(self):
        """Shows the Data Collector GUI window"""
        self.controller.showCollectData()

    def Simulation_Callback(self):
        """Shows the Simulation GUI window"""
        self.controller.showSimulation()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    StartWindow = StartWindow()
    StartWindow.show()
    sys.exit(app.exec_())
