from sklearn.decomposition import NMF
import sklearn.metrics as skm
import numpy as np
import csv

# create a matrix from a csv file
matrix = np.matrix([[0,0,0,0,0,0,0,0]])
csv_file = './prueba1Modificada.csv'
# Example matrix to factorize
# i will create a matrix of 25x8 with float numbers between 1 and 2
#matrix = np.random.rand(10000, 8)
total_energy = np.linalg.norm(matrix, 'fro',)+1

# i want to read a csv file with the data
with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        #print(csv_reader)

        # Skip the headers row
        next(csv_reader)

        # Read each row of csv file
        for row in csv_reader:
            #stack_lock.acquire()  # Acquire lock before accessing the stack
            row = np.array(row, dtype=np.float64)  # Convert the row to numpy array
            #i want to add this row to a matrix
            matrix = np.vstack([matrix, row[1:9]])
            # row = [int(item) for item in row] , to avoid use numpy
            #stack_lock.release()  # Release lock after modifying the stack

# Specify the number of components (factors) for factorization
n_components = 2

# Perform NMF
for n_components in range(2, 9):
    matrix = abs(matrix)
    print("\n\nNumber of components: ", n_components)
    model = NMF(n_components=n_components, init='random', random_state=0)
    W = model.fit_transform(np.asarray(matrix))
    H = model.components_
    Reconstructed_matrix = model.inverse_transform(W)
    print(matrix.shape, Reconstructed_matrix.shape)

    r_squared = skm.r2_score( np.asarray(Reconstructed_matrix), np.asarray(matrix))
    
    #print("err: ", 1 - (model.reconstruction_err_ / total_energy))
    vaf = 0
    vaf = 1 - (np.sum((matrix  - Reconstructed_matrix)**2))/ np.sum(matrix**2)
    print("VAF: ", vaf)
    print("R^2: ", r_squared)

    # Print the factorized matrices
    #print("Matrix W (Basis Vectors):")
    #print(W)
    print("\nMatrix H (Coefficients):")
    print(H)

# Obtain the original matrix
Calculated_matrix = np.dot(W, H)

#print("\Calculated Matrix:")
#print(Calculated_matrix)
