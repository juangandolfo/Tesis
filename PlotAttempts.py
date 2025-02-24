import json
import os
import csv
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal

AttemptResults = []

def read_calibration_file(experiment_path):
    config_file_path = os.path.join(experiment_path, 'Calibration.json')
    with open(config_file_path, 'r') as file:
        data = json.load(file)
        Threshold = np.array(data['Thresholds'])
        PeakActivation = np.array(data['Peaks'])
        SynergyBase = np.array(data['SynergyBase'])
        MusclesNumber = data['MusclesNumber']
    return Threshold, PeakActivation, SynergyBase, MusclesNumber
    
def plot_attempt(data, experiment_file, timestamps, target_muscle,atttempt_id):
    global AttemptResults
    start_index, end_index = timestamps
    target_data = []
    non_target_data = []
    # Extract rows within the given range
    for row in data[start_index:end_index + 1]:
        target_data.append(float(row[target_muscle]))  # Convert to float
        non_target_data.append(sum(float(row[i]) for i in range(len(row)) if i != target_muscle))
    mean_target = np.mean(target_data)
    mean_non_target = np.mean(non_target_data)
    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(non_target_data, target_data, color='b', alpha=0.05)
    plt.xlim(-0.3, 5)
    plt.ylim(-0.3, 3)
    plt.xlabel("Sum of Non-Target Muscle Data")
    plt.ylabel("Target Muscle Data")
    plt.title(f"Attempt : {atttempt_id}")
    plt.grid(True)
    plt.scatter(mean_non_target, mean_target, color='r', marker='x', s=100)
    
    # Filter data points where either axis value is greater than 0.3
    filtered_non_target_data = [x for i, x in enumerate(non_target_data) if x > 0.3 or target_data[i] > 0.3]
    # filtered_non_target_data = [x for x in non_target_data if x > 0.3]
    filtered_target_data = [y for i, y in enumerate(target_data) if non_target_data[i] > 0.3 or y > 0.3]
    mean_filtered_non_target = np.mean(filtered_non_target_data)
    mean_filtered_target = np.mean(filtered_target_data)
    if filtered_non_target_data and filtered_target_data:
        plt.scatter(mean_filtered_non_target, mean_filtered_target, color='y', marker='o', s=100)

    AttemptResults.append([
        atttempt_id, 
        mean_target/mean_non_target,
        np.median(mean_filtered_target/mean_filtered_non_target),
        timestamps[1]-timestamps[0]
        ])

    output_path = os.path.join(os.path.join(experiment_file), f"Attempt_{atttempt_id}.png")
    print(f"Saving plot to {output_path}")
    plt.savefig(output_path)

def read_event_times(experiment_path, processed_data, target_muscle):
    event_file_path = os.path.join(experiment_path, 'Events.json')
    
    with open(event_file_path, 'r') as file:
        events_data = json.load(file)

    for attempt in events_data:
        attempt_id = attempt['Id']
        start_time = attempt['Start']
        stop_time = attempt['Stop']
        plot_attempt(processed_data, experiment_path, (start_time, stop_time), target_muscle,attempt_id)

    plot_attempt_comparison(AttemptResults,experiment_path)

def plot_attempt_comparison(attempt_results,experiment_file):
    attempt_results = np.array(attempt_results)
    attempt_ids = attempt_results[:, 0]
    attempt_times = attempt_results[:, 3].astype(float)
    ratios = attempt_results[:, 1].astype(float)
    filtered_ratios = attempt_results[:, 2].astype(float)
    plt.figure(figsize=(8, 6))
    plt.plot(attempt_ids, ratios, color='r', marker='o')
    plt.plot(attempt_ids, filtered_ratios, color='y', linestyle='--')
    plt.xlim(-0.1, attempt_ids[-1] + 1)
    plt.ylim(-0.1, 1)
    plt.xlabel("Attempt ID")
    plt.ylabel("Target/Non-Target Ratio")
    plt.title("Attempt Comparison")
    plt.grid(True)
    output_path = os.path.join(os.path.join(experiment_file), "Attempt_Comparison.png")
    print(f"Saving plot to {output_path}")
    plt.savefig(output_path)

    # Save another figure that shows the difference in time between attempts
    plt.figure(figsize=(8, 6))
    plt.plot(attempt_ids, attempt_times, color='g', marker='x')
    plt.xlim(-0.1, attempt_ids[-1] + 1)
    plt.ylim(-0.1, np.max(attempt_times) + 1)
    plt.xlabel("Attempt ID")
    plt.ylabel("Duration (samples)")
    plt.title("Attempt Duration")
    plt.grid(True)
    output_path = os.path.join(os.path.join(experiment_file), "Attempt_Duration.png")
    print(f"Saving plot to {output_path}")
    plt.savefig(output_path)

def Rectify(RawData):
    return np.abs(RawData)

def Normalize(RectifiedData, PeakActivation, MusclesNumber, Threshold):
    zeros = np.zeros(MusclesNumber)
    RectifiedData = np.maximum(zeros, RectifiedData - Threshold)
    PeakActivation = PeakActivation - Threshold
    NormalizedData = RectifiedData / PeakActivation
    return NormalizedData

def LowPassFilter(NormalizedData, MusclesNumber):
    fs = 1000  # Sampling frequency
    cutoff = 40  # Cutoff frequency
    b, a = scipy.signal.iirfilter(N = 2, Wn = [40], ftype = 'butter',fs= fs, btype='Lowpass')
    filtered_signal = scipy.signal.filtfilt(b, a, NormalizedData, axis=0)
    return filtered_signal
      
def process_data(experiment_file, Threshold, PeakActivation, SynergyBase, MusclesNumber):
    with open(experiment_file, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first row
        RawData = np.array(list(reader)).astype(float)
        
    RectifiedData = Rectify(RawData)
    NormalizedData = Normalize(RectifiedData, PeakActivation, MusclesNumber, Threshold)
    ProcessedData = LowPassFilter(NormalizedData, MusclesNumber)
    #reshapedData = ProcessedData.reshape(-1,1)
    #SynergyActivations = np.array(MapActivation(SynergyBaseInverse,reshapedData).T)
    SynergyActivations = []

    return ProcessedData, SynergyActivations



# Main
ExperimentPath = '.\ExperimentsFiles\Experiment-20250203-262642'
Target_muscle = 0 
rawdata_file_path = os.path.join(ExperimentPath, 'RawData.csv')  
Threshold, PeakActivation, SynergyBase, MusclesNumber = read_calibration_file(ExperimentPath)
ProcessedData, SynergyActivations = process_data(rawdata_file_path, Threshold, PeakActivation, SynergyBase, MusclesNumber)
event_times = read_event_times(ExperimentPath, ProcessedData, Target_muscle)
