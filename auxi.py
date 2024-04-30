import numpy as np
from collections import deque
def Dictionary_to_matrix(dictionary):
    
    # Get the keys
    columns = list(dictionary.keys())
    # Get the data 
    rows = [dictionary[column] for column in columns]
    matriz = np.array(rows).T 
    #rows = np.array(rows)
    
    return matriz
mat = deque()
dic= {"m1":[0,1,2],
      "m2":[3,4,5],
      "m3":[6,7,8]}
mat.extend(Dictionary_to_matrix(dic))
agregar={"m1":[9,10],
      "m2":[11,12],
      "m3":[13,14]}
mat.extend(Dictionary_to_matrix(agregar))
print(mat)

synergy_CursorMap = [0,90,180,270]
CursorMovement_Gain = 50
SynergyBase = np.identity(4)
SynergyBaseInverse = np.linalg.pinv(SynergyBase)

# Convert angles from degrees to radians
angles_rad = np.radians(synergy_CursorMap)
# Calculate the x and y components of each vector
x = np.cos(angles_rad)
print(x)
y = np.sin(angles_rad)
print(y)
# Construct the projection matrix
projectionMatrix = np.matrix(np.column_stack((x, y))) 
print("proy",projectionMatrix)
a = np.dot([1,1,1,1],projectionMatrix)
b = np.ravel(np.matmul([1,1,1,1],projectionMatrix))
print("a",a)
print("b",b)



