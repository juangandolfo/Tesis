import numpy as np
import json
from sklearn.decomposition import NMF
import matplotlib.pyplot as plt
import sklearn.metrics as skm
from matplotlib.gridspec import GridSpec
import mplcursors

class GlobalParameters:
    MusclesNumber = 8  # Adjust this parameter as needed for your specific use case

def calculateSynergy(matrix):
    models = []
    H = []
    numpy_H_pinv = []
    H_Normalized = []
    output = []
    vafs = []
    outputDefined = False
    # Perform NMF
    for n_components in range(2, GlobalParameters.MusclesNumber+1):
        model = NMF(n_components=n_components, init='nndsvd', tol= 1e-5, max_iter=20000, solver='cd')
        W = model.fit_transform(matrix)
        H = np.matrix(model.components_)
        Reconstructed_matrix = model.inverse_transform(W)
        r_squared = skm.r2_score(np.asarray(matrix), np.asarray(Reconstructed_matrix))
        vaf = 1 - (np.sum((matrix - Reconstructed_matrix) ** 2) / np.sum(matrix ** 2))
        vafs.append(vaf)
        H_inv = np.linalg.pinv(H)
        models.append((n_components, H, H_inv, r_squared, vaf))
        if n_components == 2:
            output = (n_components, H, H_inv, r_squared, vafs)
        else:
            if vaf > vafs[-2]:
                output = (n_components, H, H_inv, r_squared, vafs)

    return models, vafs, output

# Create a matrix with values between 0 and 1
matrix = np.random.rand(100, GlobalParameters.MusclesNumber)

# Scale the matrix to have values between 0 and 0.5
matrix = matrix * 0.1

# Calculate synergy
models, vafs, output = calculateSynergy(matrix)

# Empty dictionary
DetectionModels = {}

for i in range(len(models)):
    key = f'{i+2} Synergies'
    value = models[i][1].tolist()
    DetectionModels[key] = value
DetectionModels['vafs'] = vafs

fig = plt.figure()  # Adjust the figsize as needed
gs = fig.add_gridspec(GlobalParameters.MusclesNumber, GlobalParameters.MusclesNumber - 1)  # 4 rows, 4 columns

subplots = []
# Define your labels array
muscle_labels = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']  # Adjust the list to match your number of muscles

for j in range(2, GlobalParameters.MusclesNumber + 1):
    for i in range(1, j + 1):
        ax = fig.add_subplot(gs[i - 1, j - 2])
        ax.bar(muscle_labels, DetectionModels[f'{j} Synergies'][i - 1], color='blue', alpha=0.6)
        subplots.append(ax)
        ax.set_ylim(0, 1)  # Set y-axis limits to be between 0 and 1
        ax.set_xlim(-0.5, GlobalParameters.MusclesNumber - 0.5)  # Adjusted to match the number of labels
        #ax.set_xticks(range(GlobalParameters.MusclesNumber))
        #ax.set_yticks([0, 0.5, 1])
        
        if i == 1:
            ax.set_title(f'{j} Synergies')
            ax.set_xlabel('Muscles')  # X-axis label
            ax.set_ylabel('Muscle Activation (%)')  # Y-axis label
            ax.set_xticklabels(muscle_labels)  # Set custom x-axis labels
            ax.set_yticklabels([str(tick) for tick in [0, 0.5, 1]])
        ''' else:
                ax.set_xticklabels([])  # Remove x-axis tick labels but keep the ticks
                ax.set_yticklabels([])  # Remove y-axis tick labels but keep the ticks
'''

ax = fig.add_subplot(gs[4:GlobalParameters.MusclesNumber + 1, 0:2])
x = list(range(2, GlobalParameters.MusclesNumber + 1))  # Number of muscles
ax.plot(x, DetectionModels['vafs'], marker='o', label='VAF Curve')
ax.set_xlabel('Number of Synergies')
ax.set_ylabel('VAF')
ax.set_title('VAF vs Model')

plt.tight_layout()
plt.subplots_adjust(hspace=0.5, wspace=0.4)  # Adjust the spacing if needed

# Add a global variable to track the zoom state
zoomed_in = False

def on_click(event):
    global zoomed_in
    ax = event.inaxes
    
    if ax in subplots:
        col_idx = subplots.index(ax) % (GlobalParameters.MusclesNumber - 1)
        
        if zoomed_in:
            for idx, subplot in enumerate(subplots):
                subplot.set_visible(True)
                subplot.set_position(gs[idx // (GlobalParameters.MusclesNumber), idx % (GlobalParameters.MusclesNumber - 1)].get_position(fig))
            zoomed_in = False
        else:
            for subplot in subplots:
                subplot.set_visible(False)
            
            for i in range(GlobalParameters.MusclesNumber - 1):
                subplot = subplots[i]
                subplot.set_visible(True)
                subplot.set_position(gs[i // (GlobalParameters.MusclesNumber), i % (GlobalParameters.MusclesNumber - 1)].get_position(fig))
            
            zoomed_in = False
        
        plt.draw()

# Connect the click event
fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()
