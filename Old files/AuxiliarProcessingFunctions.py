import numpy as np
import matplotlib.pyplot as plt

def signaltonoise(a, axis=0, ddof=0):
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m/sd)

# Generate or load your EMG signal data
# For example, let's generate a random EMG signal
np.random.seed(0)  # For reproducibility
t = np.linspace(0, 1, 1000)  # Time vector
emg_signal = np.sin(2 * np.pi * 10 * t) * 2 + 20  # Example EMG signal with larger amplitude

# Add noise to the EMG signal
noise_power = 0.3  # Lower noise power compared to signal power
noisy_emg_signal = emg_signal + np.random.normal(0, noise_power, emg_signal.shape)

# Calculate mean and standard deviation of signal and noise
mean_signal = np.mean(emg_signal)
std_signal = np.std(emg_signal)
mean_noise = np.mean(noise_power)
std_noise = np.std(noisy_emg_signal)

# Calculate SNR using your custom signal_to_noise function
snr_percentage = signaltonoise(noisy_emg_signal)
print("SNR (percentage):", snr_percentage)

# Plot the original EMG signal and the noisy EMG signal
plt.figure(figsize=(10, 5))
plt.plot(t, emg_signal, label='Original EMG Signal')
plt.plot(t, noisy_emg_signal, label='Noisy EMG Signal')
median = np.median(noisy_emg_signal)
plt.plot(t,np.ones(1000)*median)
plt.title('Original EMG Signal vs Noisy EMG Signal')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.show()


