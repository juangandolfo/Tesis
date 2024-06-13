import json
import numpy as np
import GlobalParameters as params



print(np.trunc([1.6,7.3]))


string = str(np.array[1.6,7.3])
encoded = string.encode()
#mandar

#recibir
recievedData = encoded
data = np.array(json.loads(recievedData.decode().strip()))
print(data + 1)
print(format(data))
#in the next line i will print in which data type is the variable data
print(type(data))
print(type(string))

