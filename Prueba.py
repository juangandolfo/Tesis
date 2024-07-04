import numpy as np
import subprocess 

data = []
print(data == [])


data = [[1,2,3,4,5,6,7,8,9,10]]
print(np.asarray(data)[-1])

data = [[1,2,3,4,5,6,7,8,9,10],[10,12,13,14,15,16,17,18,19,10],[20,22,23,24,25,26,27,28,29,20]]
print(np.asarray(data)[-1])

MuscleActivationsSize = np.asarray(data).shape[0]
Musclesx = 0
timeStep = 0.1


print(np.linspace(Musclesx, Musclesx + 3, MuscleActivationsSize))

x = np.linspace(Musclesx, Musclesx + 3, MuscleActivationsSize, endpoint=False)
print(x)
print(x + (x[1]-x[0]))