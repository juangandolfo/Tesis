import numpy as np
from scipy import signal
from matplotlib import pyplot

# Define parameters
G = 4000  # Gain
F = 2000  # Time constant

# Define the system transfer function
numerator = [G/F]
denominator = [1, -1]
system = signal.TransferFunction(numerator, denominator)

# Frequency range for Bode plot
w, mag, phase = signal.bode(system)

# Plot Bode magnitude and phase
pyplot.figure()
pyplot.semilogx(w, mag)    # Bode magnitude plot
pyplot.title('Bode Plot - Magnitude')
pyplot.xlabel('Frequency [radians / second]')
pyplot.ylabel('Magnitude [dB]')
pyplot.grid()

pyplot.figure()
pyplot.semilogx(w, phase)  # Bode phase plot
pyplot.title('Bode Plot - Phase')
pyplot.xlabel('Frequency [radians / second]')
pyplot.ylabel('Phase [degrees]')
pyplot.grid()

pyplot.show()
