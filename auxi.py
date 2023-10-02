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