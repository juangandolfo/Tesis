import csv
import numpy as np
from matplotlib import pyplot as plt
import SynergyDetection as sd
import pandas as pd

csv_file = 'Experiments/' + 'pruebaSinergias' + '.csv'

# Create SynergyBase matrix
SynergyBase = np.random.rand(4, 8)
SynergyBase[SynergyBase < 0.5] = 0
print(SynergyBase)
for i, row in enumerate(SynergyBase[::-1]):
    plt.subplot(4, 1, i+1)
    plt.bar(range(row.shape[0]), row)
    plt.xlabel('Musculos')
    plt.ylabel('Activacion relativa')
    plt.title('Sinergia {}'.format(i+1))
plt.show()

# Define parameters for each synergy signal
num_samples = 40000  # Number of time steps
num_periods = 5      # Number of sinusoidal periods

# Create a time vector that spans multiple periods
t = np.linspace(0, 2 * np.pi * num_periods, num_samples)  # Time values for multiple periods

# Parameters for each signal
signal_params = {
    'Signal 1': {'frequency': 0.15, 'amplitude': 0.850, 'phase_shift': 0},
    'Signal 2': {'frequency': 0.18, 'amplitude': 0.725, 'phase_shift': np.pi / 3},
    'Signal 3': {'frequency': 0.17, 'amplitude': 0.98, 'phase_shift': np.pi / 6},
    'Signal 4': {'frequency': 0.16, 'amplitude': 0.675, 'phase_shift': np.pi/5}
}

# Increase the number of harmonics
harmonics = {
    'Signal 1': 16,
    'Signal 2': 18,
    'Signal 3': 17,
    'Signal 4': 16
}

# Initialize the matrix for synergy activations
num_signals = len(signal_params)
SynergyActivations = np.zeros((num_samples, num_signals))

# Generate signals with harmonics
for i, (name, params) in enumerate(signal_params.items()):
    frequency = params['frequency']
    amplitude = params['amplitude']
    phase_shift = params['phase_shift']
    
    # Base signal
    signal = amplitude * np.sin(2 * np.pi * frequency * t + phase_shift)
    
    # Add harmonics
    num_harmonics = harmonics[name]
    for j in range(2, num_harmonics + 1):
        harmonic_frequency = j * frequency
        harmonic_amplitude = amplitude / j  # Optional scaling of harmonic amplitude
        signal += harmonic_amplitude * np.sin(2 * np.pi * harmonic_frequency * t + phase_shift)
    
    # Store the signal
    SynergyActivations[:, i] = signal

# Ensure all values are non-negative
SynergyActivations = np.maximum(SynergyActivations, 0)

# Normalize the synergy activations
# Method 1: Min-Max Normalization
min_values = SynergyActivations.min(axis=0)
max_values = SynergyActivations.max(axis=0)
SynergyActivations = (SynergyActivations - min_values) / (max_values - min_values)

# Alternatively, you can use Z-Score Normalization (comment out Min-Max and uncomment Z-Score if needed)
# Method 2: Z-Score Normalization
# mean_values = SynergyActivations.mean(axis=0)
# std_values = SynergyActivations.std(axis=0)
# SynergyActivations = (SynergyActivations - mean_values) / std_values

# Plot the normalized synergy activations with time on the x-axis
time = np.arange(num_samples) / 2148  # Convert sample index to time in seconds
for i in range(num_signals):
    plt.plot(time, SynergyActivations[:, i], label=f'Synergy {i+1}')
plt.xlabel('Time (s)')
plt.ylabel('Relative Activation')
plt.title('Normalized Sinusoidal Synergy Activations with Multiple Harmonics')
plt.legend()
plt.show()

# Define the new sinusoidal signal to multiply with SynergyActivations
new_signal_params = {'frequency': 0.2, 'amplitude': 0.5, 'phase_shift': np.pi / 4}
new_signal = new_signal_params['amplitude'] * np.sin(2 * np.pi * new_signal_params['frequency'] * t + new_signal_params['phase_shift'])

# Ensure new signal has the same number of samples as SynergyActivations
if new_signal.shape[0] != SynergyActivations.shape[0]:
    raise ValueError("The length of the new signal does not match the number of samples in SynergyActivations.")

# Multiply each column of SynergyActivations by the new sinusoidal signal
SynergyActivations *= np.abs(new_signal[:, np.newaxis])

# Plot the updated synergy activations with time on the x-axis
for i in range(num_signals):
    plt.plot(time, SynergyActivations[:, i], label=f'Synergy {i+1}')
plt.xlabel('Time (s)')
plt.ylabel('Relative Activation')
plt.title('Modified Sinusoidal Synergy Activations with New Signal')
plt.legend()
plt.show()

# Compute Muscle Activations
MusclesActivations = np.dot(SynergyActivations, SynergyBase)

# Add noise to MusclesActivations
noise_amplitude = 0.1
noise = noise_amplitude * np.random.normal(size=MusclesActivations.shape)
MusclesActivations += noise
MusclesActivations = np.maximum(MusclesActivations, 0)  # Ensure non-negative values

# Plot Muscle Activations with time on the x-axis
time = np.arange(MusclesActivations.shape[0]) / 2148  # Convert sample index to time in seconds
for i in range(MusclesActivations.shape[1]):
    plt.plot(time, MusclesActivations[:, i], color='C{}'.format(i))
    plt.xlabel('Time (s)')
    plt.ylabel('Activation')
    plt.title('Muscle Activation {}'.format(i+1))
plt.show()

# Calculate synergy models
models, vafs, output = sd.calculateSynergy(MusclesActivations)

# Save results to Excel
with pd.ExcelWriter('modelValidation.xlsx') as writer:
    df = pd.DataFrame(SynergyBase)
    df.to_excel(writer, index=False)
    start_row = SynergyBase.shape[0] + 2

    for model in models:
        df = pd.DataFrame(model[1])
        df.to_excel(writer, startrow=start_row, index=False)
        start_row = start_row + model[1].shape[0] + 2

print(vafs)
