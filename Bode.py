def plot_z_transform(b, a, fs, cutoff):
    w, h = freqz(b, a, worN=8000)
    w = w * fs / (2 * np.pi)  # Convert from rad/sample to Hz

    plt.figure(figsize=(12, 6))

    # Magnitude plot
    plt.subplot(2, 1, 1)
    plt.plot(w, 20 * np.log10(abs(h)), 'b')
    plt.axvline(cutoff, color='r', linestyle='--')  # Mark the cutoff frequency
    plt.title('Digital Filter Frequency Response')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Magnitude [dB]')
    plt.grid()
    plt.legend(['Frequency Response', f'Cutoff Frequency: {cutoff} Hz'])

    # Phase plot
    plt.subplot(2, 1, 2)
    plt.plot(w, np.angle(h), 'r')
    plt.axvline(cutoff, color='r', linestyle='--')  # Mark the cutoff frequency
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Phase [radians]')
    plt.grid()
    plt.legend(['Phase Response', f'Cutoff Frequency: {cutoff} Hz'])

    plt.tight_layout()
    plt.show()
