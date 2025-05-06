import os
from datetime import datetime

class LogHandler:
    def __init__(self, ExperimentFolder):
        ###
        # Initialize the LogHandler with the experiment folder path.
        ###

        self.ExperimentFolder = os.path.join(ExperimentFolder)
        
        # Create the log file name
        self.log_fileName = self.ExperimentFolder + "/log.txt"
        self.errorLog_fileName = self.ExperimentFolder + "/errorLog.txt"
        
        # Create log files if they do not exist
        self.CreateLogFile()

    def CreateLogFile(self):
        """
        Create a log file with the current date and time in the filename.
        """
        # Get the current date and time
        dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]        
        
        if not os.path.exists(self.log_fileName):    
            # Create the log file in the current directory
            with open(self.log_fileName, 'w') as log_file:
                log_file.write(dt_string  + " - " + "Log file created: " + self.log_fileName + "\n")
                    
        if not os.path.exists(self.errorLog_fileName):
            with open(self.errorLog_fileName, 'w') as log_file:
                log_file.write(dt_string  + " - " + "Log file created: " + self.errorLog_fileName + "\n")

    def LogMessage(self, LogMessage):
        """
        Log a message to the log file.
        """
        dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        # Append the message to the log file
        with open(self.log_fileName, 'a') as log_file:
            log_file.write(dt_string + " - " + LogMessage + "\n")
        
        return

    def LogError(self, ErrorMessage):
        """
        Log an error message to the log file.
        """
        dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Append the error message to the log file
        with open(self.errorLog_fileName, 'a') as log_file:
            log_file.write(dt_string + " - " + ErrorMessage + "\n")
    


