import numpy as np

ChannelsNumber = 8       # MusclesNumber
SynergiesNumber = 4      # Max number of synergies

modelsList = {}

for i in range(2, SynergiesNumber + 1):
    n_components = i

    # Create h_norm with repeated identity pattern
    h_norm = np.array([np.identity(ChannelsNumber)[k % ChannelsNumber] for k in range(n_components)])

    H_inv = np.linalg.pinv(h_norm)
    r_squared = np.zeros(1)
    vaf = np.zeros(1)

    modelsList[i - 2] = (n_components, h_norm, H_inv, r_squared, vaf)  # use integer key

SynergyBase = modelsList[SynergiesNumber-2][1]
SynergyBaseInverse = modelsList[SynergiesNumber-2][2]

print("SynergyBase:")
print(SynergyBase)
print(SynergyBase.shape)
print("SynergyBaseInverse:")
print(SynergyBaseInverse)
print(SynergyBaseInverse.shape)