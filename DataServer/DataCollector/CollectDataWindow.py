"""
Data Collector GUI
This is the GUI that lets you connect to a base, scan via rf for sensors, and stream data from them in real time.
"""

import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from DataServer.DataCollector.CollectDataController import *
import tkinter as tk
from tkinter import filedialog
#from Plotter import GenericPlot as gp
import DataServer.API_Parameters as params
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pymsgbox as msgbox
import os 
import json
import ExportData
import csv
import numpy as np
import time
from General.DefaultConfigGenerator import save_default_configuration



class CollectDataWindow(QWidget):
    def __init__(self,controller):
        QWidget.__init__(self)
        self.pipelinetext = "Off"
        self.controller = controller
        self.buttonPanel = self.ButtonPanel()
        self.calibration_window = CalibrationWindow(parent_window=self)
        layout = QHBoxLayout()
        self.setStyleSheet("background-color:#DDDDDD;")
        layout.addWidget(self.buttonPanel)
        self.setLayout(layout)
        self.setWindowTitle("Collect Data GUI")

        #---- Connect the controller to the GUI
        self.CallbackConnector = PlottingManagement()
    
    def is_data_empty(self, data):
        """Safely check if data is empty, handling both lists and numpy arrays"""
        if data is None:
            return True
        
        try:
            if isinstance(data, np.ndarray):
                return data.size == 0
            elif hasattr(data, '__len__'):
                return len(data) == 0
            else:
                return not bool(data)
        except Exception as e:
            print(f"[WARNING] Error checking data emptiness: {e}")
            return True
    
    def get_data_length(self, data):
        """Safely get the length of data, handling both lists and numpy arrays"""
        if data is None:
            return 0
        
        try:
            if isinstance(data, np.ndarray):
                return data.size
            elif hasattr(data, '__len__'):
                return len(data)
            else:
                return 1 if data else 0
        except Exception as e:
            print(f"[WARNING] Error getting data length: {e}")
            return 0
    
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

        connect_layout = QHBoxLayout()
        
        #---- Connect Base Button
        self.connect_base_button = QPushButton('Connect Base', self)
        self.connect_base_button.setToolTip('Connect to Delsys Base')
        self.connect_base_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.connect_base_button.objectName = 'Connect Base'
        self.connect_base_button.clicked.connect(self.connect_base_callback)
        self.connect_base_button.setStyleSheet('QPushButton {color: #000066;}')
        self.is_base_connected = False
        connect_layout.addWidget(self.connect_base_button)

        #---- Connect From File Button
        self.connect_file_button = QPushButton('Connect From File', self)
        self.connect_file_button.setToolTip('Connect using CSV file')
        self.connect_file_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.connect_file_button.objectName = 'Connect From File'
        self.connect_file_button.clicked.connect(self.connect_file_callback)
        self.connect_file_button.setStyleSheet('QPushButton {color: #000066;}')
        self.is_file_connected = False
        connect_layout.addWidget(self.connect_file_button)

        buttonLayout.addLayout(connect_layout)

        findSensor_layout = QHBoxLayout()
        
        #---- Pair Button
        self.pair_button = QPushButton('Pair', self)
        self.pair_button.setToolTip('Pair Sensors')
        self.pair_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.pair_button.objectName = 'Pair'
        self.pair_button.clicked.connect(self.pair_callback)
        self.pair_button.setStyleSheet('QPushButton:enabled {color: #000066;} QPushButton:disabled {color: #888888; background-color: #CCCCCC;}')
        self.pair_button.setEnabled(False)
        findSensor_layout.addWidget(self.pair_button)

        #---- Scan Button
        self.scan_button = QPushButton('Scan', self)
        self.scan_button.setToolTip('Scan for Sensors')
        self.scan_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.scan_button.objectName = 'Scan'
        self.scan_button.clicked.connect(self.scan_callback)
        self.scan_button.setStyleSheet('QPushButton:enabled {color: #000066;} QPushButton:disabled {color: #888888; background-color: #CCCCCC;}')
        self.scan_button.setEnabled(False)
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
        self.configure_button.setStyleSheet('QPushButton:enabled {color: #000066;} QPushButton:disabled {color: #888888; background-color: #CCCCCC;}')
        self.configure_button.setEnabled(False)
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
        self.calibration_button.setStyleSheet('QPushButton:enabled {color: #000066;} QPushButton:disabled {color: #888888; background-color: #CCCCCC;}')
        self.calibration_button.setEnabled(False)
        buttonLayout.addWidget(self.calibration_button)

        #---- Start Cursor Button
        self.cursor_button = QPushButton('Cursor Game', self)
        self.cursor_button.setToolTip('Start Cursor')
        self.cursor_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.cursor_button.objectName = 'Start Cursor'
        self.cursor_button.clicked.connect(self.start_cursor)
        self.cursor_button.setStyleSheet('QPushButton:enabled {color: #000066;} QPushButton:disabled {color: #888888; background-color: #CCCCCC;}')
        self.cursor_button.setEnabled(False)
        buttonLayout.addWidget(self.cursor_button)

        #---- Start Visualization Button
        self.visualization_button = QPushButton('Visualization', self)
        self.visualization_button.setToolTip('Start Visualization')
        self.visualization_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.visualization_button.objectName = 'Start Visualization'
        self.visualization_button.clicked.connect(self.start_visualization)
        self.visualization_button.setStyleSheet('QPushButton:enabled {color: #000066;} QPushButton:disabled {color: #888888; background-color: #CCCCCC;}')
        self.visualization_button.setEnabled(False)
        buttonLayout.addWidget(self.visualization_button)

        #---- Export Data Button
        self.export_button = QPushButton('Export Data', self)
        self.export_button.setToolTip('Export Data')
        self.export_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.export_button.objectName = 'Export Data'
        self.export_button.clicked.connect(self.export_data)
        self.export_button.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(self.export_button)

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

    def connect_base_callback(self):
        if self.is_base_connected:
            # Disconnect from base
            try:
                # Add any necessary disconnection logic here
                self.is_base_connected = False
                self.connect_base_button.setText('Connect Base')
                self.connect_base_button.setToolTip('Connect to Delsys Base')
                self.connect_file_button.setEnabled(True)
                self.reset_all_buttons_to_initial_state()
                self.pipelinestatelabel.setText("Disconnected - Ready to Connect")
            except Exception as e:
                msgbox.alert(f"Error disconnecting from base: {str(e)}")
        else:
            # Connect to base
            params.DelsysMode = True
            try:
                self.CallbackConnector.Connect_Callback()
                # If connection successful, update button states
                self.is_base_connected = True
                self.connect_base_button.setText('Disconnect Base')
                self.connect_base_button.setToolTip('Disconnect from Delsys Base')
                self.connect_file_button.setEnabled(False)
                self.scan_button.setEnabled(True)
                self.getpipelinestate()
                self.pipelinestatelabel.setText(self.pipelinetext + " (Base Connected)")
            except Exception as e:
                # Handle connection error gracefully
                msgbox.alert(f"Failed to connect to Delsys base:\n{str(e)}\n\nPlease check that:\n"
                            "- The base is powered on and connected\n"
                            "- Drivers are properly installed\n"
                            "- No other application is using the base")
                
                # Reset the connection state to allow user to try again
                self.reset_connection_state()

    def connect_file_callback(self):
        if self.is_file_connected:
            # Disconnect from file
            try:
                self.is_file_connected = False
                self.connect_file_button.setText('Connect From File')
                self.connect_file_button.setToolTip('Connect using CSV file')
                self.connect_base_button.setEnabled(True)
                self.reset_all_buttons_to_initial_state()
                self.pipelinestatelabel.setText("Disconnected - Ready to Connect")
            except Exception as e:
                msgbox.alert(f"Error disconnecting from file: {str(e)}")
        else:
            # Connect from file
            # Create a hidden tkinter root to prevent blank window
            root = tk.Tk()
            root.withdraw()  # Hide the main tkinter window
            
            # Open file dialog to select CSV file
            file_path = filedialog.askopenfilename(
                title="Select a CSV file containing muscle data to simulate connection",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            # Destroy the tkinter root to clean up
            root.destroy()
            
            if file_path:
                # Validate the CSV file
                if self.validate_csv_file(file_path):
                    params.DelsysMode = False
                    params.csvFile = file_path
                    try:
                        self.CallbackConnector.Connect_Callback()
                        # If connection successful, update button states
                        self.is_file_connected = True
                        self.connect_file_button.setText('Disconnect File')
                        self.connect_file_button.setToolTip('Disconnect from CSV file')
                        self.connect_base_button.setEnabled(False)
                        self.scan_button.setEnabled(True)
                        self.getpipelinestate()
                        self.pipelinestatelabel.setText(self.pipelinetext + " (File Connected)")
                    except Exception as e:
                        # Handle connection error gracefully
                        msgbox.alert(f"Failed to connect using CSV file:\n{str(e)}\n\nPlease try selecting a different file.")
                        self.reset_connection_state()
                # Note: Error details are now provided by validate_csv_file method

    def validate_csv_file(self, file_path):
        """Validate that the CSV file has the expected format"""
        try:
            import csv
            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file, delimiter=',')
                
                # Read header row
                try:
                    header = next(csv_reader)
                    if len(header) < 2:  # At least timestamp + one data column
                        msgbox.alert(f"CSV file error: Header row has only {len(header)} column(s).\n"
                                   f"Expected at least 2 columns (timestamp + data columns).\n"
                                   f"Header found: {header}")
                        return False
                    header_col_count = len(header)
                except StopIteration:
                    msgbox.alert("CSV file error: File appears to be empty (no header row found).")
                    return False
                
                # Check data rows
                row_count = 0
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 since header is row 1
                    if len(row) != header_col_count:
                        msgbox.alert(f"CSV file error: Row {row_num} has {len(row)} columns, "
                                   f"but header has {header_col_count} columns.\n"
                                   f"All rows must have the same number of columns.\n"
                                   f"Problem row: {row[:5]}{'...' if len(row) > 5 else ''}")
                        return False
                    
                    # Skip first column (timestamp), check remaining are numeric
                    for col_idx, value in enumerate(row[1:], start=1):
                        try:
                            float(value)
                        except ValueError:
                            col_name = header[col_idx] if col_idx < len(header) else f"Column {col_idx + 1}"
                            msgbox.alert(f"CSV file error: Non-numeric value found in row {row_num}, column '{col_name}'.\n"
                                       f"Value: '{value}'\n"
                                       f"All data columns (except the first one) must contain numeric values.\n"
                                       f"First column (timestamp) can be any value and will be ignored.")
                            return False
                    
                    row_count += 1
                    if row_count > 10:  # Check first 10 rows for performance
                        break
                
                if row_count == 0:
                    msgbox.alert("CSV file error: No data rows found after the header.\n"
                               "File must contain at least one row of data.")
                    return False
                
                return True
                
        except FileNotFoundError:
            msgbox.alert(f"CSV file error: Could not find file at path:\n{file_path}")
            return False
        except PermissionError:
            msgbox.alert(f"CSV file error: Permission denied when trying to read file:\n{file_path}\n"
                       "Please check that the file is not open in another application.")
            return False
        except Exception as e:
            msgbox.alert(f"CSV file error: Unexpected error while reading file:\n{str(e)}")
            return False

    def reset_connection_state(self):
        """Reset the UI to allow user to try connecting again"""
        self.connect_base_button.setEnabled(True)
        self.connect_file_button.setEnabled(True)
        self.connect_base_button.setText('Connect Base')
        self.connect_base_button.setToolTip('Connect to Delsys Base')
        self.connect_file_button.setText('Connect From File')
        self.connect_file_button.setToolTip('Connect using CSV file')
        self.is_base_connected = False
        self.is_file_connected = False
        self.scan_button.setEnabled(False)
        self.configure_button.setEnabled(False)
        self.calibration_button.setEnabled(False)
        self.cursor_button.setEnabled(False)
        self.visualization_button.setEnabled(False)
        self.getpipelinestate()
        self.pipelinestatelabel.setText("Connection Failed - Ready to Retry")

    def reset_all_buttons_to_initial_state(self):
        """Reset all buttons to their initial disabled state after disconnection"""
        self.scan_button.setEnabled(False)
        self.configure_button.setEnabled(False)
        self.calibration_button.setEnabled(False)
        self.cursor_button.setEnabled(False)
        self.visualization_button.setEnabled(False)

    def connect_callback(self):
        # Legacy method for backward compatibility
        self.connect_base_callback()

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
            self.configure_button.setEnabled(True)
                    
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
        self.CallbackConnector.FinishInitialization()
        # Enable calibration after sensors are configured
        self.calibration_button.setEnabled(True)

    def calibration_callback(self):
        params.StartCalibration = True
        
        # Reset calibration state to ensure stage buttons are disabled until new calibration is loaded
        self.calibration_window.reset_calibration_state()
        self.calibration_window.show()
        self.CallbackConnector.StartCalibration_Callback()
        
        # Wait for PM to create default config and auto-load it
        self.calibration_window.wait_and_load_default_config()
        
        # Don't enable visualization and cursor buttons immediately
        # They will be enabled only after a valid calibration is completed

    def enable_post_calibration_buttons(self):
        """Enable visualization and cursor buttons after successful calibration completion"""
        self.visualization_button.setEnabled(True)
        self.cursor_button.setEnabled(True)

    def start_cursor(self):
        self.CallbackConnector.StartCursor_Callback()

    def start_visualization(self):
        self.CallbackConnector.StartVisualization_Callback()
    
    def export_data(self):
        # Replace these paths with your actual local folder and OneDrive sync folder
        local_folder = r"C:\Users\melis\OneDrive\Documents\GitHub\Tesis\ExperimentsFiles"
        onedrive_folder = r"C:\Users\melis\OneDrive - Universidad Católica del Uruguay\Tesis\Etapa Caracterización\Experimental Data"
        ExportData.upload_folder_to_onedrive(local_folder, onedrive_folder)


class SimulationWindow(QWidget):
    def __init__(self, controller, config_folder):
        super(SimulationWindow, self).__init__()  # Properly call the base class initializer
        self.config_folder = config_folder
        self.controller = controller
        self.config_file = "Calibration.json"
        self.events_file = "Events.json"
        self.raw_data_file = "RawData.csv"
        self.colors = ['Red', 'Blue', 'Yellow', 'Green', 'Orange', 'Purple', 'Grey', 'Brown']

        # Create the main layout
        main_layout = QHBoxLayout()
        self.setStyleSheet("background-color:#DDDDDD;")

        # Add button panel
        self.buttonPanel = self.ButtonPanel()
        main_layout.addWidget(self.buttonPanel)

        # Add plotting area
        self.plotting_area = self.create_plotting_area()
        main_layout.addWidget(self.plotting_area)

        self.setLayout(main_layout)
        self.setWindowTitle("Simulation GUI")

        # Populate the config dropdown with experiment folders
        self.populate_config_dropdown()

        # Connect the controller to the GUI
        self.CallbackConnector = PlottingManagement()  # Replace with your actual connector if needed

    def ButtonPanel(self):
        buttonPanel = QWidget()
        buttonLayout = QVBoxLayout()

        # Configuration File Dropdown (Only Experiment Folder Selection)
        self.config_label = QLabel("Select the experiment folder:", self)
        self.config_label.setFixedSize(200, 50)
        self.config_label.setAlignment(Qt.AlignCenter)
        self.config_label.setStyleSheet("color:#000066;")
        buttonLayout.addWidget(self.config_label)

        self.config_dropdown = QComboBox(self)
        self.config_dropdown.setToolTip("Select an experiment folder")
        self.config_dropdown.setStyleSheet("QComboBox {color: #000066; background: #848482;}")
        self.config_dropdown.currentIndexChanged.connect(self.config_file_selected)
        buttonLayout.addWidget(self.config_dropdown)

        # Placeholder dropdown for attempts (hidden initially)
        self.attempts_label = QLabel("Select an attempt:", self)
        self.attempts_label.setFixedSize(200, 50)
        self.attempts_label.setAlignment(Qt.AlignCenter)
        self.attempts_label.setStyleSheet("color:#000066;")
        self.attempts_label.hide()  # Initially hidden
        buttonLayout.addWidget(self.attempts_label)

        self.attempts_dropdown = QComboBox(self)
        self.attempts_dropdown.setToolTip("Select an attempt")
        self.attempts_dropdown.setStyleSheet("QComboBox {color: #000066; background: #848482;}")
        self.attempts_dropdown.currentIndexChanged.connect(self.attempt_selected)
        self.attempts_dropdown.hide()  # Initially hidden
        buttonLayout.addWidget(self.attempts_dropdown)

        self.attempt_info_label = QLabel("Attempt details")
        self.attempt_info_label.hide()
        buttonLayout.addWidget(self.attempt_info_label)

        # Connect Button
        self.read_button = QPushButton('Read Experiment Files', self)
        self.read_button.setFixedSize(200, 50)
        self.read_button.setToolTip('Read Experiment Files')
        self.read_button.clicked.connect(self.upload_experiment)
        self.read_button.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(self.read_button)

       # Start Simulation Button
        start_simulation_button = QPushButton('Start Simulation', self)
        start_simulation_button.setFixedSize(200, 50)
        start_simulation_button.setToolTip('Start Simulation')
        start_simulation_button.clicked.connect(self.start_simulation_callback)
        start_simulation_button.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(start_simulation_button)

        # Start Simulation Cursor
        start_cursor_simulation = QPushButton('Start Cursor', self)
        start_cursor_simulation.setFixedSize(200, 50)
        start_cursor_simulation.setToolTip('Start Cursor')
        start_cursor_simulation.clicked.connect(self.start_cursor_simulation)
        start_cursor_simulation.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(start_cursor_simulation)

        # Home Button
        home_button = QPushButton('Home', self)
        home_button.setFixedSize(200, 50)
        home_button.setToolTip('Return to Start Menu')
        home_button.clicked.connect(self.home_callback)
        home_button.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(home_button)

        buttonPanel.setLayout(buttonLayout)
        return buttonPanel

    def create_plotting_area(self):
        """Create a plotting area using Matplotlib."""
        plot_widget = QWidget()
        layout = QVBoxLayout()

        # Create a Matplotlib figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)
        plot_widget.setLayout(layout)
        plot_widget.setFixedSize(1000, 800)
        return plot_widget

    def upload_experiment(self):
        # Get the selected experiment folder from the dropdown
        selected_folder = self.config_dropdown.currentText()
        self.selected_folder_path = os.path.join(self.config_folder, selected_folder)

        # Check if the specified .json configuration file exists in the selected folder
        config_file_path = os.path.join(self.selected_folder_path, self.config_file)
        if not os.path.exists(config_file_path):
            print(f"No file named {self.config_file} found in {self.selected_folder_path}")
            return
        # Read the .json file
        with open(config_file_path, 'r') as json_file:
            json_data = json.load(json_file)

        # Extract the data from the JSON into variables
        self.angles = json_data['Angles']
        self.muscles_number = json_data['MusclesNumber']
        self.peaks = json_data['Peaks']
        self.sensor_stickers = json_data['SensorStickers']
        self.synergy_base = json_data['SynergyBase']
        self.thresholds = json_data['Thresholds']
        
        # print("Angles:", self.angles)
        # print("MusclesNumber:", self.muscles_number)
        # print("Peaks:", self.peaks)
        # print("SensorStickers:", self.sensor_stickers)
        # print("SynergyBase:", self.synergy_base)
        # print("Thresholds:", self.thresholds)

        # Check if the specified .json file exists in the selected folder
        events_file_path = os.path.join(self.selected_folder_path, self.events_file)
        if not os.path.exists(events_file_path):
            print(f"No file named {self.events_file} found in {self.selected_folder_path}")
            return
        # Read the .json file
        with open(events_file_path, 'r') as json_file:
            json_data = json.load(json_file)
        
        # # Create a list to store all attempts
        # self.attempts_data = []

        # # Extract the data from the JSON into variables
        # for attempt in json_data:  # Use json_data, not json_file
        #     attempt_info = {
        #         "attemptNumber": attempt["attemptNumber"],
        #         "start_Timestamp": attempt["start_Timestamp"],
        #         "end_Timestamp": attempt["end_Timestamp"],
        #         "result": attempt["result"],
        #     }
        #     self.attempts_data.append(attempt_info)  # Append each attempt to the list

        # Print or process all attempts
        # for attempt_info in attempts_data:
        #     print(f"Attempt {attempt_info['attemptNumber']}:")
        #     print(f"  Start: {attempt_info['start_Timestamp']}")
        #     print(f"  End: {attempt_info['end_Timestamp']}")
        #     print(f"  Result: {attempt_info['result']}")

        # Populate the dropdown with attempts
        self.attempts_dropdown.clear()  # Clear any existing items
        for attempt in json_data:
            self.attempts_dropdown.addItem(f"Attempt {attempt['Id']}", attempt)

        # Show the dropdown and label
        self.attempts_label.show()
        self.attempts_dropdown.show()
        
        # Logic to handle experiment file upload and data processing
        self.plot_data()

    def plot_data(self):
        self.figure.clear()
        self.synergiesNumber = np.array(self.synergy_base).shape[0]
        gs = self.figure.add_gridspec(self.synergiesNumber, 2)  
        
        # Plot Synergy Base ----------------------------------------------
        for i in range (1, self.synergiesNumber+1):
            ax = self.figure.add_subplot(gs[i-1, 0])
            ax.bar(range(np.asarray(self.synergy_base).shape[1]), self.synergy_base[i-1], color=self.colors[i-1], alpha=0.6)
            ax.set_ylim(0, 1)  # Set y-axis limits to be between 0 and 0.5
            ax.set_xlim(-0.5, self.muscles_number-0.5) 
            ax.set_xticks(range(self.muscles_number))  # Ensure all ticks are visible
            ax.set_yticks([0, 0.5, 1])  # Ensure y-ticks are visible

            if i == 1:
                ax.set_title(f'Synergy Basis ({self.synergiesNumber} Synergies)')
                ax.set_xlabel('Muscles')  # X-axis label
                ax.set_ylabel('Relative Activation')  # Y-axis label
                ax.set_xticklabels(self.sensor_stickers)
                ax.set_yticklabels([str(tick) for tick in [0, 0.5, 1]])
            else: 
                ax.set_xticklabels([''] * self.muscles_number)  # Remove x-axis tick labels but keep the ticks
                ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
            
        # Plot Projection Angles ----------------------------------------------
        ax = self.figure.add_subplot(gs[:, 1], polar=True)
        ax.set_title("Projection Angles")
        for i in range(len(self.angles)):
            theta = np.radians(int(self.angles[i]))  # Convert to radians
            ax.plot([0, theta], [0, 1], marker='o', color=self.colors[i])  # Plot the vector
        
        # Adjust the layout to expand subplots
        self.figure.tight_layout()
        self.figure.subplots_adjust(hspace=0.8, wspace=0.6)  # Adjust the spacing if needed
        self.canvas.draw()

    def home_callback(self):
        self.controller.showStartMenu()

    def start_simulation_callback(self):
        params.csvFile = os.path.join(self.selected_folder_path, self.raw_data_file)

        self.CallbackConnector.Connect_Callback()
        time.sleep(0.1)
        self.CallbackConnector.Scan_Callback()
        time.sleep(0.1)
        self.CallbackConnector.setSampleMode_hardcoded()
        time.sleep(0.1)
        self.CallbackConnector.StartCalibration_Callback()
        
        #UploadCalibration 
        params.Thresholds = self.thresholds
        params.Peaks = self.peaks
        params.AnglesOutput = self.angles
        params.SynergyBase = self.synergy_base
        params.SensorStickers = self.sensor_stickers
        params.SynergiesNumber = len(self.angles)
        params.SimulationCalibration = True
        time.sleep(1)
        self.CallbackConnector.StartCursor_Callback()
        
    
    def start_cursor_simulation(self):
        self.CallbackConnector.StartCursor_Callback()

    def config_file_selected(self, index):
        """Callback function triggered when a folder is selected."""
        if index >= 0:  # Ensure a valid selection
            selected_folder = self.config_dropdown.itemText(index)
            selected_path = os.path.join(self.config_folder, selected_folder)
            print(f"Selected Experiment Folder: {selected_path}")

    def populate_config_dropdown(self):
        """Populates the dropdown with experiment folders."""
        if not os.path.exists(self.config_folder):
            print(f"Error: Config folder '{self.config_folder}' does not exist.")
            return

        # List subfolders (experiment folders)
        experiment_folders = [f for f in os.listdir(self.config_folder) if os.path.isdir(os.path.join(self.config_folder, f))]

        if not experiment_folders:
            print("No experiment folders found.")
            return

        # Add experiment folders to the dropdown
        self.config_dropdown.clear()  # Clear previous items
        self.config_dropdown.addItems(experiment_folders)

    def attempt_selected(self, index):
        self.attempt_info_label.show()
        if index >= 0:
            selected_attempt = self.attempts_dropdown.itemData(index)
            
            # This is an example of the data you can display (replace it with actual data from the attempt)
            attempt_data = f"Attempt {index+1} details:\n"
            attempt_data += f"Start: {selected_attempt['Start']}\n"
            attempt_data += f"End: {selected_attempt['Stop']}\n"
            attempt_data += f"Result: {selected_attempt['Result']}"

            # Update the label to show the corresponding data for the selected attempt
            self.attempt_info_label.setText(attempt_data)

    
class CountdownWidget(QWidget):

    timeout_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.timer_label = QLabel(f"Remaining time: {params.remaining_time}")
        self.timer_label.setStyleSheet('color: #000066;')
        layout.addWidget(self.timer_label)
        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def start_countdown(self):
        if params.CalibrationStage == 1:
            params.remaining_time = params.TimeCalibStage1
        if params.CalibrationStage == 2:
            params.remaining_time = params.TimeCalibStage2
        if params.CalibrationStage == 3:
            params.remaining_time = params.TimeCalibStage3

        self.remaining_time = params.remaining_time
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
            params.CalibrationStageInitialized = False
            params.CalibrationStageFinished = True

class CalibrationWindow(QMainWindow):

    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window  # Reference to CollectDataWindow
        self.setWindowTitle("Calibration Window")
        self.setGeometry(100, 100, 1400, 800)  # Make window larger to accommodate all visualizations
        self.CalibrationStage = 0

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        self.setStyleSheet("background-color:#DDDDDD;")

        layout = QVBoxLayout()

        # Move upload button to top and reorganize button order
        self.upload_calibration_button = QPushButton("Upload Last Calibration")
        self.upload_calibration_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.upload_calibration_button.setStyleSheet('QPushButton {color: #000066;}')

        self.stage1_button = QPushButton("1 - Base Noise")
        self.stage1_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.stage1_button.setStyleSheet('QPushButton:enabled {color: #000066;} QPushButton:disabled {color: #888888; background-color: #CCCCCC;}')
        self.stage1_button.setEnabled(False)  # Initially disabled

        self.stage2_button = QPushButton("2 - Maximum Activations")
        self.stage2_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.stage2_button.setStyleSheet('QPushButton:enabled {color: #000066;} QPushButton:disabled {color: #888888; background-color: #CCCCCC;}')
        self.stage2_button.setEnabled(False)  # Initially disabled
        
        self.stage3_button = QPushButton("3 - Synergy Basis")
        self.stage3_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.stage3_button.setStyleSheet('QPushButton:enabled {color: #000066;} QPushButton:disabled {color: #888888; background-color: #CCCCCC;}')
        self.stage3_button.setEnabled(False)  # Initially disabled

        self.choose_projection_button = QPushButton("Choose Projection")
        self.choose_projection_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.choose_projection_button.setStyleSheet('QPushButton {color: #000066;}')
        
        self.terminate_button = QPushButton("Terminate Calibration")
        self.terminate_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.terminate_button.setStyleSheet('QPushButton {color: #000066;}')
        
        self.set_synergy_base = QPushButton("Set Synergies Basis")
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
        
        self.sensors_dropdown = QComboBox(self)
        self.sensors_dropdown.setToolTip("Select a muscle to calibrate:")
        self.sensors_dropdown.setStyleSheet("QComboBox {color: #000066; background: #848482;}")
        self.sensors_dropdown.currentIndexChanged.connect(self.sensor_selected)
        self.sensors_dropdown.hide()
        self.sensors_dropdown_label = QTextBrowser()
        self.sensors_dropdown_label.hide()
        
        self.timer_widget = CountdownWidget()
        self.timer_widget.hide()  # Initially hide the CountdownWidget

        # Connect buttons to callbacks - all enabled simultaneously
        self.upload_calibration_button.clicked.connect(self.stage4_callback)
        self.stage1_button.clicked.connect(self.stage1_callback)
        self.stage2_button.clicked.connect(self.stage2_callback)
        self.stage3_button.clicked.connect(self.stage3_callback)
        self.choose_projection_button.clicked.connect(self.show_select_model)
        self.terminate_button.clicked.connect(self.terminate_callback)

        # Connect Start button to start countdown
        self.start_stage_button.clicked.connect(self.start_countdown)
        self.set_synergy_base.clicked.connect(self.set_model)

        # Create figure with 4 subplots for comprehensive visualization
        self.figure = plt.figure(figsize=(14, 10)) 
        self.canvas = FigureCanvas(self.figure)
        self.colors = ['Red', 'Blue', 'Yellow', 'Green', 'Orange', 'Purple', 'Grey', 'Brown']
        
        # Initialize default visualization
        self.init_default_visualization()
        
        params.PlotCalibrationSignal.signal.connect(self.update_plot_with_debug)

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
        
        #Construct the layout - Upload button first, then calibration steps
        layout.addWidget(self.upload_calibration_button)
        layout.addWidget(self.stage1_button)
        layout.addWidget(self.stage2_button)
        layout.addWidget(self.stage3_button)
        layout.addWidget(self.choose_projection_button)
        layout.addWidget(self.stage_message_label)
        layout.addWidget(self.sensors_dropdown)
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
        
        # Initialize calibration state
        self.calibration_loaded = False

    def wait_and_load_default_config(self):
        """Wait for PM to create default config file and auto-load it"""
        print(f"[DEBUG] wait_and_load_default_config called")
        
        # First wait for experiment timestamp to be created
        timestamp_timeout = 3.0
        timestamp_elapsed = 0.0
        check_interval = 0.1
        
        print(f"[DEBUG] Waiting for experiment timestamp...")
        while timestamp_elapsed < timestamp_timeout:
            print(f"[DEBUG] ExperimentTimestamp: '{params.ExperimentTimestamp}', ChannelsNumber: {params.ChannelsNumber}")
            
            if params.ExperimentTimestamp and params.ChannelsNumber:
                print(f"[DEBUG] Experiment timestamp and channel count available")
                break
                
            time.sleep(check_interval)
            timestamp_elapsed += check_interval
        
        if not params.ExperimentTimestamp or not params.ChannelsNumber:
            print("[DEBUG] No experiment timestamp or channel count available after waiting, skipping auto-load")
            return
            
        # Construct expected default config file path
        experiment_folder = f'ExperimentsFiles/Experiment-{params.ExperimentTimestamp}'
        default_config_file = os.path.join(experiment_folder, f'Default_{params.ChannelsNumber}muscle_Calibration.json')
        
        print(f"[DEBUG] Waiting for default config file: {default_config_file}")
        
        # Wait for file to be created with timeout
        timeout = 5.0  # 5 seconds timeout
        elapsed_time = 0.0
        
        while elapsed_time < timeout:
            print(f"[DEBUG] Checking for file existence... elapsed: {elapsed_time:.1f}s")
            if os.path.exists(default_config_file):
                print(f"[DEBUG] Default config file found, triggering stage 4 flow...")
                try:
                    # Set the file path for stage 4 to use
                    params.SelectedCalibrationFilePath = default_config_file
                    
                    # Trigger the standard stage 4 flow (same as when user clicks stage 4)
                    params.CalibrationStage = 4
                    params.CalibrationStageInitialized = True
                    
                    print(f"[DEBUG] Stage 4 flow triggered for auto-loading: {default_config_file}")
                    
                    # Enable stage buttons since we're loading a calibration
                    self.calibration_loaded = True
                    self.enable_stage_buttons()
                    
                    return
                    
                except Exception as e:
                    print(f"[WARNING] Failed to trigger stage 4 for default configuration: {e}")
                    break
            
            time.sleep(check_interval)
            elapsed_time += check_interval
        
        if elapsed_time >= timeout:
            print(f"[WARNING] Timeout reached waiting for default config file: {default_config_file}")
            print(f"[DEBUG] Final check - file exists: {os.path.exists(default_config_file)}")
            msgbox.alert(f"Warning: Could not find or load default configuration file.\n\nExpected file: {default_config_file}\n\nPlease use 'Upload Last Calibration' to manually load a configuration file.")

    def enable_stage_buttons(self):
        """Enable stage buttons after successful calibration loading"""
        self.stage1_button.setEnabled(True)
        self.stage2_button.setEnabled(True)
        self.stage3_button.setEnabled(True)

    def disable_stage_buttons(self):
        """Disable stage buttons when no calibration is loaded"""
        self.stage1_button.setEnabled(False)
        self.stage2_button.setEnabled(False)
        self.stage3_button.setEnabled(False)

    def reset_calibration_state(self):
        """Reset calibration state - disable stage buttons"""
        self.calibration_loaded = False
        self.disable_stage_buttons()

    def is_data_empty(self, data):
        """Safely check if data is empty, handling both lists and numpy arrays"""
        if data is None:
            return True
        
        try:
            if isinstance(data, np.ndarray):
                return data.size == 0
            elif hasattr(data, '__len__'):
                return len(data) == 0
            else:
                return not bool(data)
        except Exception as e:
            print(f"[WARNING] Error checking data emptiness: {e}")
            return True
    
    def get_data_length(self, data):
        """Safely get the length of data, handling both lists and numpy arrays"""
        if data is None:
            return 0
        
        try:
            if isinstance(data, np.ndarray):
                return data.size
            elif hasattr(data, '__len__'):
                return len(data)
            else:
                return 1 if data else 0
        except Exception as e:
            print(f"[WARNING] Error getting data length: {e}")
            return 0

    def init_default_visualization(self):
        """Initialize the default visualization with 4 subplots showing default/empty states"""
        try:
            self.figure.clear()
            
            # Create 2x2 subplot grid
            self.ax_thresholds = self.figure.add_subplot(2, 2, 1)
            self.ax_peaks = self.figure.add_subplot(2, 2, 2) 
            self.ax_synergies = self.figure.add_subplot(2, 2, 3)
            self.ax_directions = self.figure.add_subplot(2, 2, 4, polar=True)
            
            # Initialize default data
            default_muscles = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']
            default_thresholds = [0.05] * 8
            default_peaks = [0.5] * 8
            default_synergies = [[0.2, 0.8, 0.1, 0.3, 0.6, 0.4, 0.7, 0.2],
                                [0.7, 0.2, 0.5, 0.8, 0.1, 0.6, 0.3, 0.9]]
            default_angles = [0, 90]
            
            # Plot default thresholds
            self.ax_thresholds.bar(default_muscles, default_thresholds, color='#1A4207', alpha=0.6)
            self.ax_thresholds.set_title('Thresholds (Default)')
            self.ax_thresholds.set_ylabel('Activation (mV)')
            self.ax_thresholds.tick_params(axis='x', rotation=45)
            
            # Plot default peaks
            self.ax_peaks.bar(default_muscles, default_peaks, color='#1A4207', alpha=0.6)
            # Add default thresholds overlay
            self.ax_peaks.bar(default_muscles, default_thresholds, color='#808080', alpha=0.7)
            self.ax_peaks.set_title('Peaks vs Thresholds (Default)')
            self.ax_peaks.set_ylabel('Activation (mV)')
            self.ax_peaks.tick_params(axis='x', rotation=45)
            
            # Plot default synergies
            for i, synergy in enumerate(default_synergies):
                self.ax_synergies.bar([x + i*0.4 for x in range(len(default_muscles))], 
                                    synergy, width=0.35, color=self.colors[i], 
                                    alpha=0.6, label=f'Synergy {i+1}')
            self.ax_synergies.set_title('Synergy Basis (Default)')
            self.ax_synergies.set_ylabel('Relative Activation')
            self.ax_synergies.set_xticks(range(len(default_muscles)))
            self.ax_synergies.set_xticklabels(default_muscles)
            self.ax_synergies.legend()
            
            # Plot default directions
            for i, angle in enumerate(default_angles):
                theta = np.radians(angle)
                self.ax_directions.plot([0, theta], [0, 1], marker='o', 
                                      color=self.colors[i], linewidth=2, 
                                      markersize=8, label=f'Synergy {i+1}')
            self.ax_directions.set_title('Projection Angles (Default)')
            self.ax_directions.legend()
            
            # Adjust layout and draw
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize default visualization: {e}")
            msgbox.alert(f"Error initializing calibration visualization: {str(e)}")

    def update_thresholds_subplot(self):
        """Update only the thresholds subplot"""
        try:
            if not self.is_data_empty(params.Thresholds) and not self.is_data_empty(params.SensorStickers):
                self.ax_thresholds.clear()
                data = params.Thresholds
                self.ax_thresholds.bar(params.SensorStickers, data, color="#1A4207")
                
                # Color code based on threshold values
                for i, value in enumerate(data):
                    if value > 0.1:
                        self.ax_thresholds.bar(params.SensorStickers[i], value, color="#B11E1E")
                    elif 0.08 < value <= 0.1:
                        self.ax_thresholds.bar(params.SensorStickers[i], value, color="#B46A0F")
                
                self.ax_thresholds.set_title('Detected Thresholds')
                self.ax_thresholds.set_ylabel('Muscle Activation (mV)')
                self.ax_thresholds.tick_params(axis='x', rotation=45)
                self.canvas.draw()
        except Exception as e:
            print(f"[ERROR] Failed to update thresholds subplot: {e}")

    def update_peaks_subplot(self):
        """Update only the peaks subplot"""
        try:
            if not self.is_data_empty(params.Peaks) and not self.is_data_empty(params.SensorStickers):
                self.ax_peaks.clear()
                data = params.Peaks
                self.ax_peaks.bar(params.SensorStickers, data, color="#1A4207")
                
                # Color code based on peak values
                for i, value in enumerate(data):
                    if value < 0.3:
                        self.ax_peaks.bar(params.SensorStickers[i], value, color="#B11E1E")
                    elif 0.3 <= value < 0.5:
                        self.ax_peaks.bar(params.SensorStickers[i], value, color="#B46A0F")
                
                # Add thresholds overlay if available
                if not self.is_data_empty(params.Thresholds):
                    thresholds = params.Thresholds
                    self.ax_peaks.bar(params.SensorStickers, thresholds, color="#808080", alpha=0.7)
                    
                    # Add SNR text
                    for i, (peak, threshold) in enumerate(zip(data, thresholds)):
                        if threshold > 0:
                            snr = peak / threshold
                            self.ax_peaks.text(i, peak + 0.01, f'SNR: {snr:.1f}', 
                                             ha='center', va='bottom', fontsize=8, fontweight='bold')
                
                self.ax_peaks.set_title('Detected Peaks vs Thresholds')
                self.ax_peaks.set_ylabel('Muscle Activation (mV)')
                self.ax_peaks.tick_params(axis='x', rotation=45)
                self.canvas.draw()
        except Exception as e:
            print(f"[ERROR] Failed to update peaks subplot: {e}")

    def update_synergies_subplot(self):
        """Update only the synergies subplot"""
        try:
            if not self.is_data_empty(params.SynergyBase) and hasattr(params, 'SynergiesNumber'):
                self.ax_synergies.clear()
                synergy_data = np.array(params.SynergyBase)
                
                if len(synergy_data.shape) == 2:
                    width = 0.8 / params.SynergiesNumber
                    muscle_indices = np.arange(synergy_data.shape[1])
                    
                    for i in range(params.SynergiesNumber):
                        offset = (i - params.SynergiesNumber/2 + 0.5) * width
                        self.ax_synergies.bar(muscle_indices + offset, synergy_data[i], 
                                            width=width, color=self.colors[i % len(self.colors)], 
                                            alpha=0.7, label=f'Synergy {i+1}')
                    
                    self.ax_synergies.set_title(f'Synergy Basis ({params.SynergiesNumber} Synergies)')
                    self.ax_synergies.set_ylabel('Relative Activation')
                    self.ax_synergies.set_xticks(muscle_indices)
                    if not self.is_data_empty(params.SensorStickers):
                        self.ax_synergies.set_xticklabels(params.SensorStickers[:synergy_data.shape[1]], rotation=45)
                    self.ax_synergies.legend()
                    self.ax_synergies.set_ylim(0, 1)
                    
                self.canvas.draw()
        except Exception as e:
            print(f"[ERROR] Failed to update synergies subplot: {e}")

    def update_directions_subplot(self):
        """Update only the directions subplot"""
        try:
            if not self.is_data_empty(params.AnglesOutput):
                self.ax_directions.clear()
                angles = [int(angle) for angle in params.AnglesOutput if str(angle).isdigit()]
                
                for i, angle in enumerate(angles):
                    theta = np.radians(angle)
                    self.ax_directions.plot([0, theta], [0, 1], marker='o', 
                                          color=self.colors[i % len(self.colors)], 
                                          linewidth=3, markersize=10, 
                                          label=f'Synergy {i+1}: {angle}°')
                
                self.ax_directions.set_title('Projection Angles')
                self.ax_directions.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
                self.canvas.draw()
        except Exception as e:
            print(f"[ERROR] Failed to update directions subplot: {e}")

    def stage1_callback(self):
        self.save_button.hide()
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].hide()
            self.angle_labels[i].hide()
        self.synergies_lineedit_label.hide()
        self.synergy_base_lineedit.hide()
        self.set_synergy_base.hide()

        self.stage_message_label.show()
        self.start_stage_button.show()
        self.sensors_dropdown.show()
        
        self.stage_message_label.setText("Calibration Stage 1: Activation Threshold Detection \nHold as still as possible to detect the baseline noise of each sensor. Try not to activate any muscles during the countdown.")
        
        self.populate_sensors_dropdown()
        self.CalibrationStage = 1
      

    def stage2_callback(self):
        self.save_button.hide()
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].hide()
            self.angle_labels[i].hide()
        self.synergies_lineedit_label.hide()
        self.synergy_base_lineedit.hide()
        self.set_synergy_base.hide()

        self.stage_message_label.show()
        self.start_stage_button.show()
        self.sensors_dropdown.show()

        self.stage_message_label.setText("Calibration Stage 2: Activation Peaks Detection \nTry to activate each muscle to its maximum during the countdown to determine the maximum activation.")
       
        self.populate_sensors_dropdown()
        self.CalibrationStage = 2
        

    def stage3_callback(self):
        self.save_button.hide()
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].hide()
            self.angle_labels[i].hide()
        self.synergies_lineedit_label.hide()
        self.synergy_base_lineedit.hide()
        self.set_synergy_base.hide()
        self.sensors_dropdown.hide()

        self.stage_message_label.show()
        self.start_stage_button.show()
        
        self.stage_message_label.setText("Calibration Stage 3: Synergies Detection \nIn this stage, muscle synergies will be detected. During the countdown, try to activate all the involved muscles with random movements.")
      
        self.CalibrationStage = 3
        

    def stage4_callback(self):
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].hide()
            self.angle_labels[i].hide()
        self.save_button.hide()
        self.synergies_lineedit_label.hide()
        self.synergy_base_lineedit.hide()
        self.set_synergy_base.hide()
        self.sensors_dropdown.hide()

        self.stage_message_label.show()
        self.start_stage_button.show()
        
        # File selection logic
        default_file = os.path.join(os.getcwd(), "Configuration.json")
        
        if os.path.exists(default_file):
            # Configuration.json exists - ask user if they want to use it or browse
            reply = msgbox.confirm(
                f"Configuration.json found in the root folder.\n\nDo you want to use this file?\n\nClick 'OK' to use Configuration.json or 'Cancel' to browse for another file.",
                "Configuration File Selection",
                buttons=["OK", "Cancel"]
            )
            
            if reply == "OK":
                selected_file = default_file
            else:
                # User wants to browse for a different file
                root = tk.Tk()
                root.withdraw()  # Hide the main window
                selected_file = filedialog.askopenfilename(
                    title="Select Configuration File",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialdir=os.getcwd()
                )
                root.destroy()
                
                if not selected_file:  # User cancelled file selection
                    self.stage_message_label.setText("No file selected. Please try again.")
                    self.start_stage_button.hide()
                    return
        else:
            # Configuration.json doesn't exist - show file browser
            msgbox.alert(
                "Configuration.json not found in the root folder.\n\nPlease select a configuration file.",
                "File Not Found"
            )
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            selected_file = filedialog.askopenfilename(
                title="Select Configuration File",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=os.getcwd()
            )
            root.destroy()
            
            if not selected_file:  # User cancelled file selection
                self.stage_message_label.setText("No file selected. Please try again.")
                self.start_stage_button.hide()
                return
        
        # Store the selected file path
        params.SelectedCalibrationFilePath = selected_file
        filename = os.path.basename(selected_file)
        
        # Reset calibration state when starting new calibration loading
        self.reset_calibration_state()
        
        self.stage_message_label.setText(f"Press Start to upload the calibration from:\n{filename}")
        
        self.CalibrationStage = 4
        

    def start_countdown(self):
        print("timer")
        # Show the countdown widget and start the countdown
        params.CalibrationStage = self.CalibrationStage
        params.CalibrationStageInitialized = True
        if self.CalibrationStage == 4:
            pass
        else:
            self.timer_widget.timer_label.show()
            self.timer_widget.show()
            self.timer_widget.start_countdown()
    
    def sensor_selected(self, index):
        if index >= 0:
            selected_sensor = self.sensors_dropdown.itemText(index)
            params.selectedSensorIndex = index
            

    def populate_sensors_dropdown(self):
        self.sensors_dropdown.clear()
        self.sensors_dropdown.addItems(['All'])
        self.sensors_dropdown.addItems(params.SensorStickers)

    def terminate_callback (self):
        params.TerminateCalibrationFlag = True
        # try:
        #     params.SaveCalibrationToJson(
        #                                         params.ChannelsNumber,
        #                                         params.Thresholds,
        #                                         params.Peaks,
        #                                         params.AnglesOutput,
        #                                         params.SynergyBase,
        #                                         params.SensorStickers
        #                                         )
        # except Exception as e:
        #     msgbox.alert(e)
        self.close()

    def show_select_model(self):
        self.start_stage_button.hide()
        self.stage_message_label.hide()
        self.sensors_dropdown.hide()
        self.timer_widget.timer_label.hide()

        params.CalibrationStage = 6
        
        self.synergies_lineedit_label.show()
        self.synergy_base_lineedit.show()
        self.set_synergy_base.show()

        params.PlotModels = True
        try:
            print("[DEBUG] Calling update_plot from show_select_model")
            self.update_plot()
        except Exception as e:
            print(f"[ERROR] Error in show_select_model: {e}")
            msgbox.alert(f"Error displaying synergy models: {str(e)}")

    def show_angle_window(self):
        self.save_button.show()
        params.AnglesOutput = []
        # Show the AngleWindow only in stage 3
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].show()
            self.angle_labels[i].show()
        params.PlotAngles = True
        try:
            print("[DEBUG] Calling update_plot from show_angle_window")
            self.update_plot()
        except Exception as e:
            print(f"[ERROR] Error in show_angle_window: {e}")
            msgbox.alert(f"Error displaying angle selection: {str(e)}")

    def update_plot(self):
        print("[DEBUG] update_plot() called")
        
        # Check if calibration data is loaded and enable stage buttons
        if (not self.is_data_empty(params.Thresholds) and 
            not self.is_data_empty(params.Peaks) and 
            not self.is_data_empty(params.SynergyBase) and 
            not self.is_data_empty(params.AnglesOutput) and
            not self.calibration_loaded):
            self.calibration_loaded = True
            self.enable_stage_buttons()
            print("[DEBUG] Calibration data loaded - stage buttons enabled")
        
        try:
            if params.PlotThresholds:
                print("[DEBUG] Updating thresholds subplot")
                self.update_thresholds_subplot()
                params.PlotThresholds = False
                
            elif params.PlotPeaks:
                print("[DEBUG] Updating peaks subplot")
                self.update_peaks_subplot()
                params.PlotPeaks = False

            elif params.PlotModels:
                print("[DEBUG] Plotting models")
                print(f"[DEBUG] ChannelsNumber: {params.ChannelsNumber}")
                print(f"[DEBUG] SynergiesModels type: {type(params.SynergiesModels)}")
                print(f"[DEBUG] SynergiesModels keys: {list(params.SynergiesModels.keys()) if isinstance(params.SynergiesModels, dict) else 'Not a dict'}")
                
                # Check if SynergiesModels data exists
                models_available = False
                if params.SynergiesModels is not None:
                    if isinstance(params.SynergiesModels, dict):
                        models_available = len(params.SynergiesModels) > 0
                    elif hasattr(params.SynergiesModels, '__len__'):
                        models_available = len(params.SynergiesModels) > 0
                    else:
                        models_available = bool(params.SynergiesModels)
                
                if not models_available:
                    print("[ERROR] SynergiesModels data is empty or None")
                    msgbox.alert("Cannot plot models: No synergy models available")
                    return
                    
                if params.ChannelsNumber < 2:
                    print(f"[ERROR] Invalid ChannelsNumber: {params.ChannelsNumber}")
                    msgbox.alert(f"Cannot plot models: Invalid channel count ({params.ChannelsNumber})")
                    return
                
                try:
                    self.figure.clear()            
                    data = params.SynergiesModels
                    gs = self.figure.add_gridspec(params.ChannelsNumber + 1, params.ChannelsNumber - 1)  

                    subplots = []
                    for j in range(2, params.ChannelsNumber + 1):
                        model_key = f'{j} Synergies'
                        if model_key not in data:
                            print(f"[WARNING] Missing model key: {model_key}")
                            continue
                            
                        for i in range (1, j+1):
                            try:
                                ax = self.figure.add_subplot(gs[i-1, j-2])
                                ax.bar([str(index) for index in range(1, params.ChannelsNumber + 1)], data[model_key][i-1], color='#00008B', alpha=0.6)
                                subplots.append(ax)
                                ax.set_ylim(0, 1)  # Set y-axis limits to be between 0 and 0.5
                                ax.set_xlim(-0.5, params.ChannelsNumber-0.5) 
                                ax.set_xticks(range(params.ChannelsNumber))  # Ensure all ticks are visible
                                ax.set_yticks([0, 0.5, 1])  # Ensure y-ticks are visible
                                if i == 1:
                                    ax.set_title(f'{j} Synergies')
                                    if j == 2:
                                        ax.set_xlabel('Muscles')  # X-axis label
                                        ax.set_ylabel('Relative Activation')  # Y-axis label
                                        if params.SensorStickers:
                                            ax.set_xticklabels(params.SensorStickers)
                                        ax.set_yticklabels([str(tick) for tick in [0, 0.5, 1]])
                                    else:
                                        ax.set_xticklabels([''] * params.ChannelsNumber)  # Remove x-axis tick labels but keep the ticks
                                        ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
                                else:
                                    ax.set_xticklabels([''] * params.ChannelsNumber)  # Remove x-axis tick labels but keep the ticks
                                    ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
                            except Exception as subplot_error:
                                print(f"[ERROR] Failed to create subplot for {j} synergies, component {i}: {subplot_error}")
                                continue
                                
                    # Plot VAF curve
                    try:
                        ax = self.figure.add_subplot(gs[params.ChannelsNumber , 0])
                        x = list(range(2, params.ChannelsNumber+1))  # Number of muscles
                        if 'vafs' in data:
                            ax.plot(x, data['vafs'], marker='o', label='VAF Curve')
                            ax.set_xlabel('Number of Synergies')
                            ax.set_ylabel('VAF (%)')
                            ax.set_title('VAF vs Model')

                            # Ensure the x-axis contains only integers
                            ax.set_xticks(np.arange(2, params.ChannelsNumber + 1, 1))  # Set x-ticks from 2 to the number of channels
                            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: '{:d}'.format(int(x))))  # Ensure x-ticks are displayed as integers
                        else:
                            print("[WARNING] No VAF data available for plotting")
                    except Exception as vaf_error:
                        print(f"[ERROR] Failed to plot VAF curve: {vaf_error}")

                    # Adjust the layout to expand subplots
                    self.figure.tight_layout()
                    self.figure.subplots_adjust(hspace=0.8, wspace=0.6)  # Adjust the spacing if needed
                    self.canvas.draw()
                    print("[DEBUG] Models plot completed successfully")
                    params.PlotModels = False
                except Exception as e:
                    print(f"[ERROR] Failed to plot models: {e}")
                    msgbox.alert(f"Failed to plot models: {str(e)}")
                    params.PlotModels = False
                    
            elif params.PlotAngles:
                print("[DEBUG] Updating comprehensive display with angles")
                # Recreate comprehensive display
                self.init_default_visualization()
                # Update all subplots with current data
                self.update_thresholds_subplot()
                self.update_peaks_subplot()
                self.update_synergies_subplot()
                self.update_directions_subplot()
                
            elif params.PlotUploadedConfig:
                print("[DEBUG] Updating comprehensive display with uploaded config")
                # Recreate comprehensive display
                self.init_default_visualization()
                # Update all subplots with current data
                self.update_thresholds_subplot()
                self.update_peaks_subplot()
                self.update_synergies_subplot()
                self.update_directions_subplot()
                params.PlotUploadedConfig = False
                
                # Enable visualization and cursor buttons after successful calibration upload
                if self.parent_window:
                    self.parent_window.enable_post_calibration_buttons()
                    
            else:
                print("[DEBUG] No valid plot mode detected")
                print(f"[DEBUG] PlotThresholds: {params.PlotThresholds}")
                print(f"[DEBUG] PlotPeaks: {params.PlotPeaks}")
                print(f"[DEBUG] PlotModels: {params.PlotModels}")
                print(f"[DEBUG] PlotAngles: {params.PlotAngles}")
                print(f"[DEBUG] PlotUploadedConfig: {params.PlotUploadedConfig}")

        except Exception as main_error:
            print(f"[ERROR] Critical error in update_plot: {main_error}")
            msgbox.alert(f"Critical plotting error: {str(main_error)}\n\nPlease check the console for details.")
        
        print("[DEBUG] update_plot() finished")
    
    def update_plot_with_debug(self):
        """Debug wrapper for update_plot called by signal"""
        print("[DEBUG] update_plot_with_debug() called via signal")
        print(f"[DEBUG] Signal triggered - PlotThresholds: {params.PlotThresholds}")
        print(f"[DEBUG] Signal triggered - PlotPeaks: {params.PlotPeaks}")
        print(f"[DEBUG] Signal triggered - PlotModels: {params.PlotModels}")
        try:
            self.update_plot()
        except Exception as e:
            print(f"[ERROR] Error in signal-triggered update_plot: {e}")
            msgbox.alert(f"Error updating plot via signal: {str(e)}")
    
    def set_model(self):
        self.SynergiesNumber = int(self.synergy_base_lineedit.text())
        if self.SynergiesNumber >= 2 and self.SynergiesNumber <= params.ChannelsNumber:
            params.SynergiesNumber = self.SynergiesNumber
            params.SynergyBase = params.SynergiesModels[f'{self.SynergiesNumber} Synergies']
            self.show_angle_window()
           
        else: 
            msgbox.alert("Invalid number of synegies. Close this window and choose the number of synergies again.")

    def save_angles(self):
        AnglesOutput = []
        AnglesCount = 0
        angles = [lineedit.text() for lineedit in self.angle_lineedits]
        for angle in angles:
            if angle != '':
                AnglesCount = AnglesCount + 1
                AnglesOutput.append(angle)
        if AnglesCount != params.SynergiesNumber:
            msgbox.alert("The number of angles doesn't match with the number of synegies selected. Choose the angles again.")
            self.show_angle_window()
        else:
            params.PlotAngles = False
            params.AnglesOutputSemaphore.acquire()
            params.AnglesReady = 1
            params.AnglesOutput = AnglesOutput
            params.AnglesOutputSemaphore.release()
            
            # Enable visualization and cursor buttons after successful calibration completion
            if self.parent_window:
                self.parent_window.enable_post_calibration_buttons()
           
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    CollectDataWindow = CollectDataWindow()
    CollectDataWindow.show()
    sys.exit(app.exec_())



