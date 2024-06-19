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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pymsgbox as msgbox


class CollectDataWindow(QWidget):
    def __init__(self,controller):
        QWidget.__init__(self)
        self.pipelinetext = "Off"
        self.controller = controller
        self.buttonPanel = self.ButtonPanel()
        self.calibration_window = CalibrationWindow()
        layout = QHBoxLayout()
        self.setStyleSheet("background-color:#DDDDDD;")
        layout.addWidget(self.buttonPanel)
        self.setLayout(layout)
        self.setWindowTitle("Collect Data GUI")

        #---- Connect the controller to the GUI
        self.CallbackConnector = PlottingManagement()

    #-----------------------------------------------------------------------
    #---- GUI Components
    def ButtonPanel(self):
        buttonPanel = QWidget()
        buttonLayout = QVBoxLayout()

        self.pipelinelabel = QLabel('Pipeline State', self)
        self.pipelinelabel.setAlignment(Qt.AlignCenter)
        self.pipelinelabel.setStyleSheet("color:#000066")
        buttonLayout.addWidget(self.pipelinelabel)

        self.pipelinestatelabel = QLabel(self.pipelinetext, self)
        self.pipelinestatelabel.setAlignment(Qt.AlignCenter)
        self.pipelinestatelabel.setStyleSheet("color:#000066")
        buttonLayout.addWidget(self.pipelinestatelabel)

        #---- Connect Button
        self.connect_button = QPushButton('Connect', self)
        self.connect_button.setToolTip('Connect Base')
        self.connect_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.connect_button.objectName = 'Connect'
        self.connect_button.clicked.connect(self.connect_callback)
        self.connect_button.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(self.connect_button)

        findSensor_layout = QHBoxLayout()
        
        #---- Pair Button
        self.pair_button = QPushButton('Pair', self)
        self.pair_button.setToolTip('Pair Sensors')
        self.pair_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.pair_button.objectName = 'Pair'
        self.pair_button.clicked.connect(self.pair_callback)
        self.pair_button.setStyleSheet('QPushButton {color: #000066;}')
        self.pair_button.setEnabled(False)
        findSensor_layout.addWidget(self.pair_button)

        #---- Scan Button
        self.scan_button = QPushButton('Scan', self)
        self.scan_button.setToolTip('Scan for Sensors')
        self.scan_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.scan_button.objectName = 'Scan'
        self.scan_button.clicked.connect(self.scan_callback)
        self.scan_button.setStyleSheet('QPushButton {color: #000066;}')
        self.scan_button.setEnabled(True)
        findSensor_layout.addWidget(self.scan_button)

        buttonLayout.addLayout(findSensor_layout)

        ''' #---- Start Button
        self.start_button = QPushButton('Start', self)
        self.start_button.setToolTip('Start Sensor Stream')
        self.start_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.start_button.objectName = 'Start'
        self.start_button.clicked.connect(self.start_callback)
        self.start_button.setStyleSheet('QPushButton {color: #000066;}')
        self.start_button.setEnabled(False)
        buttonLayout.addWidget(self.start_button)'''

        '''#---- Stop Button
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setToolTip('Stop Sensor Stream')
        self.stop_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.stop_button.objectName = 'Stop'
        self.stop_button.clicked.connect(self.stop_callback)
        self.stop_button.setStyleSheet('QPushButton {color: #000066;}')
        self.stop_button.setEnabled(False)
        buttonLayout.addWidget(self.stop_button)'''

        '''#---- Reset Button
        self.reset_button = QPushButton('Reset Pipeline', self)
        self.reset_button.setToolTip('Disarm Pipeline')
        self.reset_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.reset_button.objectName = 'Reset'
        self.reset_button.clicked.connect(self.reset_callback)
        self.reset_button.setStyleSheet('QPushButton {color: #000066;}')
        self.reset_button.setEnabled(False)
        buttonLayout.addWidget(self.reset_button)'''

        #---- Configure Sensors Button
        self.configure_button = QPushButton('Configure Sensors', self)
        self.configure_button.setToolTip('Configure Sensors')
        self.configure_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.configure_button.objectName = 'Configure Sensors'
        self.configure_button.clicked.connect(self.ConfigureSensors_callback)  # Connect to the callback method
        self.configure_button.setStyleSheet('QPushButton {color: #000066;}')
        self.configure_button.setEnabled(True)
        buttonLayout.addWidget(self.configure_button)

        '''#---- Drop-down menu of sensor modes
        self.SensorModeList = QComboBox(self)
        self.SensorModeList.setToolTip('Sensor Modes')
        self.SensorModeList.objectName = 'PlaceHolder'
        self.SensorModeList.setStyleSheet('QComboBox {color: #000066;background: #848482}')
        self.SensorModeList.currentIndexChanged.connect(self.sensorModeList_callback)
        #buttonLayout.addWidget(self.SensorModeList)'''

        #---- List of detected sensors
        self.SensorListBox = QListWidget(self)
        self.SensorListBox.setToolTip('Sensor List')
        self.SensorListBox.objectName = 'PlaceHolder'
        self.SensorListBox.setStyleSheet('QListWidget {color: #000066;background:#848482}')
        #self.SensorListBox.clicked.connect(self.sensorList_callback)
        buttonLayout.addWidget(self.SensorListBox)

         #---- Calibration Button
        self.calibration_button = QPushButton('Start Calibration', self)
        self.calibration_button.setToolTip('Start Calibration')
        self.calibration_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.calibration_button.objectName = 'Start Calibration'
        self.calibration_button.clicked.connect(self.calibration_callback)  # Connect to the callback method
        self.calibration_button.setStyleSheet('QPushButton {color: #000066;}')
        self.calibration_button.setEnabled(False)
        buttonLayout.addWidget(self.calibration_button)

        #---- Start Cursor Button
        self.cursor_button = QPushButton('Cursor Game', self)
        self.cursor_button.setToolTip('Start Cursor')
        self.cursor_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.cursor_button.objectName = 'Start Cursor'
        self.cursor_button.clicked.connect(self.start_cursor)
        self.cursor_button.setStyleSheet('QPushButton {color: #000066;}')
        self.cursor_button.setEnabled(False)
        buttonLayout.addWidget(self.cursor_button)

        #---- Start Visualization Button
        self.visualization_button = QPushButton('Visualization', self)
        self.visualization_button.setToolTip('Start Visualization')
        self.visualization_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.visualization_button.objectName = 'Start Visualization'
        self.visualization_button.clicked.connect(self.start_visualization)
        self.visualization_button.setStyleSheet('QPushButton {color: #000066;}')
        self.visualization_button.setEnabled(False)
        buttonLayout.addWidget(self.visualization_button)

        #---- Home Button
        button = QPushButton('Home', self)
        button.setToolTip('Return to Start Menu')
        button.objectName = 'Home'
        button.clicked.connect(self.home_callback)
        button.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(button)

        buttonPanel.setLayout(buttonLayout)

        return buttonPanel

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
    
    def ConfigureSensors_callback(self):
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
        self.timer_label = QLabel("Remaining time: 5")
        self.timer_label.setStyleSheet('color: #000066;')
        layout.addWidget(self.timer_label)
        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        #self.remaining_time = 30

    def start_countdown(self):
        self.remaining_time = 5
        self.timer_label.setText(f"Remaining time: {self.remaining_time}")
        self.timer.start(1000)

    def update_timer(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            self.timer_label.setText(f"Remaining time: {self.remaining_time}")
        else:
            self.timer.stop()
            self.timer_label.setText("Timeout")
            self.timeout_signal.emit()
            API_Parameters.CalibrationStageInitialized = False
            API_Parameters.CalibrationStageFinished = True

class CalibrationWindow(QMainWindow):

    #PlotCalibrationSignal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibration Window")
        self.setGeometry(100, 100, 800, 600)
        self.CalibrationStage = 0

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        self.setStyleSheet("background-color:#DDDDDD;")

        layout = QVBoxLayout()

        self.stage1_button = QPushButton("Stage 1")
        self.stage1_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.stage1_button.setStyleSheet('QPushButton {color: #000066;}')
        self.stage2_button = QPushButton("Stage 2")
        self.stage2_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.stage2_button.setStyleSheet('QPushButton {color: #000066;}')
        self.stage3_button = QPushButton("Stage 3")
        self.stage3_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.stage3_button.setStyleSheet('QPushButton {color: #000066;}')
        self.upload_calibration_button = QPushButton("Upload Last Calibration")
        self.upload_calibration_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.upload_calibration_button.setStyleSheet('QPushButton {color: #000066;}')
        self.terminate_button = QPushButton("Terminate Calibration")
        self.terminate_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.terminate_button.setStyleSheet('QPushButton {color: #000066;}')
        self.set_synergy_base = QPushButton("Set Synergies Base")
        self.set_synergy_base.setFixedSize(240, 30)  # Set a fixed size for the button
        self.set_synergy_base.setStyleSheet('QPushButton {color: #000066;}')
        self.set_synergy_base.hide()

        self.synergies_lineedit_label = QLabel("Select the number of synergies:")
        self.synergies_lineedit_label.setStyleSheet('color: #000066;')
        self.synergy_base_lineedit = QLineEdit()
        self.synergy_base_lineedit.setFixedWidth(100)
        self.synergy_base_lineedit.hide()
        self.synergies_lineedit_label.hide()
        
        #self.stage_message_label = QLabel("")
        self.stage_message_label = QTextBrowser()
        self.stage_message_label.setStyleSheet('color: #000066;')
        self.stage_message_label.setFixedWidth(240)
        
        # Initialize Start buttons for each stage
        self.start_stage_button = QPushButton("Start")
        self.start_stage_button.setStyleSheet('QPushButton {color: #000066;}')
        self.start_stage_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.start_stage_button.hide()  # Initially hide the Start button
        
        self.timer_widget = CountdownWidget()
        self.timer_widget.hide()  # Initially hide the CountdownWidget

        self.stage1_button.clicked.connect(self.stage1_callback)
        self.stage2_button.clicked.connect(self.stage2_callback)
        self.stage3_button.clicked.connect(self.stage3_callback)
        self.upload_calibration_button.clicked.connect(self.stage4_callback)
        self.terminate_button.clicked.connect(self.terminate_callback)

        # Connect Start button to start countdown
        self.start_stage_button.clicked.connect(self.start_countdown)
        self.set_synergy_base.clicked.connect(self.set_model)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        API_Parameters.PlotCalibrationSignal.signal.connect(self.update_plot)

        # Angles selection window
        angles_layout = QVBoxLayout()

        self.angle_lineedits = []
        self.angle_labels = []
        for i in range(8):
            angle_label = QLabel(f"Synergy {i+1}:")
            angle_label.setStyleSheet('color: #000066;')
            angle_lineedit = QLineEdit()
            angle_lineedit.setFixedWidth(100)
            angle_lineedit.hide()
            angle_label.hide()
            self.angle_lineedits.append(angle_lineedit)
            self.angle_labels.append(angle_label)
            angles_layout.addWidget(angle_label)
            angles_layout.addWidget(angle_lineedit)
            # Connect the textChanged signal to the update_plot method
            angle_lineedit.textChanged.connect(self.update_plot)

        self.save_button = QPushButton("Save Angles")
        self.save_button.setFixedWidth(100)
        self.save_button.setStyleSheet('QPushButton {color: #000066;}')
        self.save_button.hide()
        self.save_button.clicked.connect(self.save_angles)

        angles_layout.addWidget(self.save_button)
        
        #Construct the layout 
        layout.addWidget(self.stage1_button)
        layout.addWidget(self.stage2_button)
        layout.addWidget(self.stage3_button)
        layout.addWidget(self.upload_calibration_button)
        layout.addWidget(self.stage_message_label)
        layout.addWidget(self.start_stage_button)
        layout.addWidget(self.timer_widget)
        layout.addWidget(self.synergies_lineedit_label)
        layout.addWidget(self.synergy_base_lineedit)
        layout.addWidget(self.set_synergy_base)
        layout.addLayout(angles_layout)
        layout.addWidget(self.terminate_button)
        main_layout.addLayout(layout)
        main_layout.addWidget(self.canvas)
        main_layout.setStretch(1, 1)

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
    
    def stage4_callback(self):
        self.stage_message_label.setText("Uploading calibration file ...")
        # Show Start button for Stage 3 only
        self.start_stage_button.show()
        self.CalibrationStage = 4
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
        self.save_button.show()
        API_Parameters.AnglesOutput = []
        # Show the AngleWindow only in stage 3
        if API_Parameters.CalibrationStage == 3:
            for i in range(API_Parameters.SynergiesNumber):
                self.angle_lineedits[i].show()
                self.angle_labels[i].show()
        API_Parameters.PlotAngles = True
        self.update_plot()

    def update_plot(self):
        self.figure.clear()

        if API_Parameters.PlotThresholds:
            ax = self.figure.add_subplot(111)
            self.muscles_number = API_Parameters.ChannelsNumber
            self.muscles_name = [f'Muscle {i+1}' for i in range(self.muscles_number)]  # Generate muscle names
            bar_width = 0.3 
            #positions = np.arange(len(self.muscles_name)) * 100 
            data = API_Parameters.Thresholds 
            ax.bar(self.muscles_name, data, color = '#00008B')
            ax.set_xlabel('Muscles')  # X-axis label
            ax.set_ylabel('Muscle Activation (mV)')  # Y-axis label
            ax.set_title('Detected thresholds')  # Plot title
            #ax.set_xticks(positions)
            #ax.set_xticklabels(self.muscles_name, rotation=45, ha='right') 
            API_Parameters.PlotThresholds = False
            
        elif API_Parameters.PlotPeaks:
            ax = self.figure.add_subplot(111)
            self.muscles_number = API_Parameters.ChannelsNumber
            self.muscles_name = [f'Muscle {i+1}' for i in range(self.muscles_number)]  # Generate muscle names
            bar_width = 0.3 
            #positions = np.arange(len(self.muscles_name)) * 100 
            data = API_Parameters.Peaks 
            ax.bar(self.muscles_name, data, color = '#00008B')
            ax.set_xlabel('Muscles')  # X-axis label
            ax.set_ylabel('Muscle Activation (mV)')  # Y-axis label
            ax.set_title('Detected Peaks')  # Plot title
            API_Parameters.PlotPeaks = False

        elif API_Parameters.PlotModels:
            data = API_Parameters.SynergiesModels
            gs = self.figure.add_gridspec(API_Parameters.ChannelsNumber, API_Parameters.ChannelsNumber - 1)  # 4 rows, 4 columns

            subplots = []
            for j in range(2, API_Parameters.ChannelsNumber + 1):
                for i in range (1, j+1):
                    ax = self.figure.add_subplot(gs[i-1, j-2])
                    ax.bar([str(index) for index in range(1, API_Parameters.ChannelsNumber + 1)], data[f'{j} Synergies'][i-1], color='#00008B', alpha=0.6)
                    ax.set_xlabel('Muscles')  # X-axis label
                    ax.set_ylabel('Muscle Activation (%)')  # Y-axis label
                    subplots.append(ax)
                    if i == 1:
                        ax.set_title(f'{j} Synergies')

            #plt.tight_layout()  # Ensures subplots are nicely spaced
            self.synergies_lineedit_label.show()
            self.synergy_base_lineedit.show()
            self.set_synergy_base.show()
            API_Parameters.PlotModels = False

        elif API_Parameters.PlotAngles:
            angles = [lineedit.text() for lineedit in self.angle_lineedits]
            try:
                angles = [int(angle) for angle in angles if angle]
            except ValueError:
                return  # Ignore invalid input
            
            ax = self.figure.add_subplot(111, polar=True)
            

            for angle in angles:
                theta = np.radians(angle)  # Convert to radians
                ax.plot([0, theta], [0, 1], marker='o')  # Plot the vector
            ax.set_title("Choose the projection angle of each synergy")

        else:
            msgbox.alert("Invalid Plot Mode")

        self.figure.tight_layout() 
        self.canvas.draw()
    
    def set_model(self):
        self.SynergiesNumber = int(self.synergy_base_lineedit.text())
        if self.SynergiesNumber >= 2 and self.SynergiesNumber <= API_Parameters.ChannelsNumber:
            API_Parameters.SynergiesNumber = self.SynergiesNumber
            self.show_angle_window()
        else: 
            msgbox.alert("Invalid number of synegies. Close this window and choose the number of synergies again.")

    def save_angles(self):
        angles = [lineedit.text() for lineedit in self.angle_lineedits]
        API_Parameters.PlotAngles = False
        API_Parameters.AnglesOutputSemaphore.acquire()
        API_Parameters.AnglesReady = 1
        API_Parameters.AnglesOutput = angles
        API_Parameters.AnglesOutputSemaphore.release()

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    CollectDataWindow = CollectDataWindow()
    CollectDataWindow.show()
    sys.exit(app.exec_())



