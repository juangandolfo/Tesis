import csv
import numpy as np
from matplotlib import pyplot as plt
import SynergyDetection as sd
import pandas as pd


csv_file = 'Experiments/' + 'pruebaSinergias' + '.csv'

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

SynergyActivations = np.zeros((1,4))

with open(csv_file, 'r') as file:
    csv_reader = csv.reader(file, delimiter=';')
    next(csv_reader)
    c = 0
    for row in csv_reader:
        SynergyActivations = np.vstack((SynergyActivations, np.array(row, dtype=np.float64)))
        c += 1
SynergyActivations = SynergyActivations[1:]  # Remove the initial zeros row
# plot Synergy activations columns
for i in range(SynergyActivations.shape[1]):
    # plt.subplot(2, 2, i+1)
    plt.plot(SynergyActivations[:, i], color='C{}'.format(i))
    plt.xlabel('Time')
    plt.ylabel('Activation')
    plt.title('Synergy {}'.format(i+1))
plt.show()

MusclesActivations = np.dot(SynergyActivations, SynergyBase)
print(MusclesActivations.shape)
for i in range(MusclesActivations.shape[1]):
    plt.plot(MusclesActivations[:, i], color='C{}'.format(i))
    plt.xlabel('Time')
    plt.ylabel('Activation')
    plt.title('Synergy {}'.format(i+1))
plt.show()


models, vafs, output =  sd.calculateSynergy(MusclesActivations)
with pd.ExcelWriter('modelValidation.xlsx') as writer:
    
    df = pd.DataFrame(SynergyBase)
    df.to_excel(writer, index=False)
    start_row = SynergyBase.shape[0]+2 
    
    for model in models:
        df = pd.DataFrame(model[1])
        df.to_excel(writer, startrow=start_row,index=False)
        start_row = start_row + model[1].shape[0] + 2
    


print("ok")
    
    




    

