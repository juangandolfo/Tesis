"""
Data Collector GUI
This is the GUI that lets you connect to a base, scan via rf for sensors, and stream data from them in real time.
"""

import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from DataCollector.CollectDataController import *
import tkinter as tk
from tkinter import filedialog
from Plotter import GenericPlot as gp
import API_Parameters

class CollectDataWindow(QWidget):
    def __init__(self,controller):
        QWidget.__init__(self)
        self.pipelinetext = "Off"
        self.controller = controller
        self.buttonPanel = self.ButtonPanel()
        self.calibration_window = CalibrationWindow()
        self.plotPanel = self.Plotter()
        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.buttonPanel)
        self.splitter.addWidget(self.plotPanel)
        layout = QHBoxLayout()
        self.setStyleSheet("background-color:#3d4c51;")
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        self.setWindowTitle("Collect Data GUI")

        #---- Connect the controller to the GUI
        self.CallbackConnector = PlottingManagement(self.plotCanvas)


    #-----------------------------------------------------------------------
    #---- GUI Components
    def ButtonPanel(self):
        buttonPanel = QWidget()
        buttonLayout = QVBoxLayout()

        self.pipelinelabel = QLabel('Pipeline State', self)
        self.pipelinelabel.setAlignment(Qt.AlignCenter)
        self.pipelinelabel.setStyleSheet("color:white")
        buttonLayout.addWidget(self.pipelinelabel)

        self.pipelinestatelabel = QLabel(self.pipelinetext, self)
        self.pipelinestatelabel.setAlignment(Qt.AlignCenter)
        self.pipelinestatelabel.setStyleSheet("color:white")
        buttonLayout.addWidget(self.pipelinestatelabel)

        #---- Connect Button
        self.connect_button = QPushButton('Connect', self)
        self.connect_button.setToolTip('Connect Base')
        self.connect_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.connect_button.objectName = 'Connect'
        self.connect_button.clicked.connect(self.connect_callback)
        self.connect_button.setStyleSheet('QPushButton {color: white;}')
        buttonLayout.addWidget(self.connect_button)

        findSensor_layout = QHBoxLayout()

        #---- Pair Button
        self.pair_button = QPushButton('Pair', self)
        self.pair_button.setToolTip('Pair Sensors')
        self.pair_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.pair_button.objectName = 'Pair'
        self.pair_button.clicked.connect(self.pair_callback)
        self.pair_button.setStyleSheet('QPushButton {color: white;}')
        self.pair_button.setEnabled(False)
        findSensor_layout.addWidget(self.pair_button)

        #---- Scan Button
        self.scan_button = QPushButton('Scan', self)
        self.scan_button.setToolTip('Scan for Sensors')
        self.scan_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.scan_button.objectName = 'Scan'
        self.scan_button.clicked.connect(self.scan_callback)
        self.scan_button.setStyleSheet('QPushButton {color: white;}')
        self.scan_button.setEnabled(True)
        findSensor_layout.addWidget(self.scan_button)

        buttonLayout.addLayout(findSensor_layout)

        ''' #---- Start Button
        self.start_button = QPushButton('Start', self)
        self.start_button.setToolTip('Start Sensor Stream')
        self.start_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.start_button.objectName = 'Start'
        self.start_button.clicked.connect(self.start_callback)
        self.start_button.setStyleSheet('QPushButton {color: white;}')
        self.start_button.setEnabled(False)
        buttonLayout.addWidget(self.start_button)'''

        '''#---- Stop Button
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setToolTip('Stop Sensor Stream')
        self.stop_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.stop_button.objectName = 'Stop'
        self.stop_button.clicked.connect(self.stop_callback)
        self.stop_button.setStyleSheet('QPushButton {color: white;}')
        self.stop_button.setEnabled(False)
        buttonLayout.addWidget(self.stop_button)'''

        '''#---- Reset Button
        self.reset_button = QPushButton('Reset Pipeline', self)
        self.reset_button.setToolTip('Disarm Pipeline')
        self.reset_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.reset_button.objectName = 'Reset'
        self.reset_button.clicked.connect(self.reset_callback)
        self.reset_button.setStyleSheet('QPushButton {color: white;}')
        self.reset_button.setEnabled(False)
        buttonLayout.addWidget(self.reset_button)'''

        #---- Calibration Button
        self.calibration_button = QPushButton('Start Calibration', self)
        self.calibration_button.setToolTip('Start Calibration')
        self.calibration_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.calibration_button.objectName = 'Start Calibration'
        self.calibration_button.clicked.connect(self.calibration_callback)  # Connect to the callback method
        self.calibration_button.setStyleSheet('QPushButton {color: white;}')
        self.calibration_button.setEnabled(False)
        buttonLayout.addWidget(self.calibration_button)

        #---- Drop-down menu of sensor modes
        self.SensorModeList = QComboBox(self)
        self.SensorModeList.setToolTip('Sensor Modes')
        self.SensorModeList.objectName = 'PlaceHolder'
        self.SensorModeList.setStyleSheet('QComboBox {color: white;background: #848482}')
        self.SensorModeList.currentIndexChanged.connect(self.sensorModeList_callback)
        buttonLayout.addWidget(self.SensorModeList)

        #---- List of detected sensors
        self.SensorListBox = QListWidget(self)
        self.SensorListBox.setToolTip('Sensor List')
        self.SensorListBox.objectName = 'PlaceHolder'
        self.SensorListBox.setStyleSheet('QListWidget {color: white;background:#848482}')
        self.SensorListBox.clicked.connect(self.sensorList_callback)
        buttonLayout.addWidget(self.SensorListBox)

        #---- Start Cursor Button
        self.cursor_button = QPushButton('Cursor Game', self)
        self.cursor_button.setToolTip('Start Cursor')
        self.cursor_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.cursor_button.objectName = 'Start Cursor'
        self.cursor_button.clicked.connect(self.start_cursor)
        self.cursor_button.setStyleSheet('QPushButton {color: white;}')
        self.cursor_button.setEnabled(False)
        buttonLayout.addWidget(self.cursor_button)

        #---- Start Visualization Button
        self.visualization_button = QPushButton('Visualization', self)
        self.visualization_button.setToolTip('Start Visualization')
        self.visualization_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.visualization_button.objectName = 'Start Visualization'
        self.visualization_button.clicked.connect(self.start_visualization)
        self.visualization_button.setStyleSheet('QPushButton {color: white;}')
        self.visualization_button.setEnabled(False)
        buttonLayout.addWidget(self.visualization_button)

        #---- Home Button
        button = QPushButton('Home', self)
        button.setToolTip('Return to Start Menu')
        button.objectName = 'Home'
        button.clicked.connect(self.home_callback)
        button.setStyleSheet('QPushButton {color: white;}')
        buttonLayout.addWidget(button)

        buttonPanel.setLayout(buttonLayout)

        return buttonPanel

    def Plotter(self):
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        plot_mode = 'windowed'                 # Select between 'scrolling' and 'windowed'
        pc = gp.GenericPlot(plot_mode)
        pc.native.objectName = 'vispyCanvas'
        pc.native.parent = self
        widget.layout().addWidget(pc.native)
        self.plotCanvas = pc
        return widget

    #-----------------------------------------------------------------------
    #---- Callback Functions
    def getpipelinestate(self):
        self.pipelinetext = self.CallbackConnector.PipelineState_Callback()
        self.pipelinestatelabel.setText(self.pipelinetext)

    def connect_callback(self):
        self.CallbackConnector.Connect_Callback()
        self.connect_button.setEnabled(False)

        self.pair_button.setEnabled(True)
        self.scan_button.setEnabled(True)
        self.getpipelinestate()
        self.pipelinestatelabel.setText(self.pipelinetext + " (Base Connected)")

    def pair_callback(self):
        self.CallbackConnector.Pair_Callback()
        self.scan_callback()
        self.getpipelinestate()

    def scan_callback(self):
        sensorList = self.CallbackConnector.Scan_Callback()
        self.SensorListBox.clear()
        self.SensorListBox.addItems(sensorList)
        self.SensorListBox.setCurrentRow(0)

        if len(sensorList)>0:
            self.calibration_button.setEnabled(True)
        self.getpipelinestate()

    '''def start_callback(self):
        self.CallbackConnector.Start_Callback()'''

    '''def stop_callback(self):
        self.CallbackConnector.Stop_Callback()
        self.reset_button.setEnabled(True)
        self.getpipelinestate()'''

    '''def reset_callback(self):
        self.CallbackConnector.Reset_Callback()
        self.getpipelinestate()
        self.reset_button.setEnabled(False)'''

    def home_callback(self):
        self.controller.showStartMenu()

    def sensorList_callback(self):
        curItem = self.SensorListBox.currentRow()
        modeList = self.CallbackConnector.getSampleModes(curItem)
        curModes = self.CallbackConnector.getCurMode()

        self.SensorModeList.clear()
        self.SensorModeList.addItems(modeList)
        self.SensorModeList.setCurrentText(curModes[0])

    def sensorModeList_callback(self):
        curItem = self.SensorListBox.currentRow()
        selMode = self.SensorModeList.currentText()
        if selMode != '':
            self.CallbackConnector.setSampleMode_hardcoded()

    def calibration_callback(self):
        self.calibration_window.show()
        self.CallbackConnector.StartCalibration_Callback()
        self.visualization_button.setEnabled(True)
        self.cursor_button.setEnabled(True)

    def start_cursor(self):
        self.CallbackConnector.StartCursor_Callback()

    def start_visualization(self):
        self.CallbackConnector.StartVisualization_Callback()


class CountdownWidget(QWidget):

    timeout_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.timer_label = QLabel("Countdown: 5")
        layout.addWidget(self.timer_label)
        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        #self.remaining_time = 30

    def start_countdown(self):
        self.remaining_time = 5
        self.timer_label.setText(f"Countdown: {self.remaining_time}")
        self.timer.start(1000)

    def update_timer(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            self.timer_label.setText(f"Countdown: {self.remaining_time}")
        else:
            self.timer.stop()
            self.timer_label.setText("Countdown: Done")
            self.timeout_signal.emit()
            API_Parameters.CalibrationStageInitialized = False
            API_Parameters.CalibrationStageFinished = True

class AngleWindow(QDialog, QObject):
    angle_values_saved = Signal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Angle Values")

        layout = QVBoxLayout()

        self.angle_lineedits = []
        self.angle_labels = []
        for i in range(8):
            angle_label = QLabel(f"Synergy {i+1}:")
            angle_lineedit = QLineEdit()
            angle_lineedit.hide()
            angle_label.hide()
            self.angle_lineedits.append(angle_lineedit)
            self.angle_labels.append(angle_label)
            layout.addWidget(angle_label)
            layout.addWidget(angle_lineedit)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_angles)
        layout.addWidget(save_button)

        self.setLayout(layout)

        self.angle_values_saved.connect(self.process_angles)  # Connect signal to method

    def save_angles(self):
        angles = [lineedit.text() for lineedit in self.angle_lineedits]
        self.angle_values_saved.emit(angles)
        self.accept()  # Close the window

    def process_angles(self, angles):
        API_Parameters.AnglesOutputSemaphore.acquire()
        API_Parameters.AnglesReady = 1
        API_Parameters.AnglesOutput = angles
        API_Parameters.AnglesOutputSemaphore.release()
        # Do something with the angle values


class CalibrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibration Window")
        self.setGeometry(100, 100, 400, 200)
        self.CalibrationStage = 0

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.stage1_button = QPushButton("Stage 1")
        self.stage2_button = QPushButton("Stage 2")
        self.stage3_button = QPushButton("Stage 3")
        self.terminate_button = QPushButton("Terminate Calibration")

        layout.addWidget(self.stage1_button)
        layout.addWidget(self.stage2_button)
        layout.addWidget(self.stage3_button)
        layout.addWidget(self.terminate_button)

        self.stage_message_label = QLabel("")
        layout.addWidget(self.stage_message_label)

        # Initialize Start buttons for each stage
        self.start_stage_button = QPushButton("Start")
        self.start_stage_button.hide()  # Initially hide the Start button
        layout.addWidget(self.start_stage_button)

        self.timer_widget = CountdownWidget()
        self.timer_widget.hide()  # Initially hide the CountdownWidget
        self.timer_widget.timeout_signal.connect(self.show_angle_window)
        layout.addWidget(self.timer_widget)

        # Angles selection window
        self.angle_window = AngleWindow()
        self.angle_window.hide()  # Initially hide the AngleWindow
        layout.addWidget(self.angle_window)

        self.stage1_button.clicked.connect(self.stage1_callback)
        self.stage2_button.clicked.connect(self.stage2_callback)
        self.stage3_button.clicked.connect(self.stage3_callback)
        self.terminate_button.clicked.connect(self.terminate_callback)

        # Connect Start button to start countdown
        self.start_stage_button.clicked.connect(self.start_countdown)

    def stage1_callback(self):
        self.stage_message_label.setText("Calibration Stage 1: Activation Threshold Detection")
        # Show Start button for Stage 1 only
        self.start_stage_button.show()
        self.CalibrationStage = 1
        self.timer_widget.hide()  #Hide the countdown widget when stage changes

    def stage2_callback(self):
        self.stage_message_label.setText("Calibration Stage 2: Activation Peaks Detection")
        # Show Start button for Stage 2 only
        self.start_stage_button.show()
        self.CalibrationStage = 2
        self.timer_widget.hide()  # Hide the countdown widget when stage changes

    def stage3_callback(self):
        self.stage_message_label.setText("Calibration Stage 3: Synergies Detection")
        # Show Start button for Stage 3 only
        self.start_stage_button.show()
        self.CalibrationStage = 3
        self.timer_widget.hide()  # Hide the countdown widget when stage changes

    def start_countdown(self):
        print("timer")
        # Show the countdown widget and start the countdown
        API_Parameters.CalibrationStage = self.CalibrationStage
        API_Parameters.CalibrationStageInitialized = True
        self.timer_widget.show()
        self.timer_widget.start_countdown()

    def terminate_callback (self):
        API_Parameters.TerminateCalibrationFlag = True
        self.close()

    def show_angle_window(self):
        API_Parameters.AnglesOutput = []
        # Show the AngleWindow only in stage 3
        if API_Parameters.CalibrationStage == 3:
            self.angle_window.show()
            for i in range(API_Parameters.ChannelsNumber):
                self.angle_window.angle_lineedits[i].show()
                self.angle_window.angle_labels[i].show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    CollectDataWindow = CollectDataWindow()
    CollectDataWindow.show()
    sys.exit(app.exec_())