from sklearn.decomposition import NMF
from sklearn.metrics import r2_score
import numpy as np

# Example matrix to factorize
# i will create a matrix of 25x8 with float numbers between 1 and 2
matrix = np.random.rand(10000, 8)
total_energy = np.linalg.norm(matrix, 'fro',)

# Specify the number of components (factors) for factorization
n_components = 2

# Perform NMF
for n_components in range(2, 9):
    print("\n\nNumber of components: ", n_components)
    model = NMF(n_components=n_components, init='random', random_state=0)
    W = model.fit_transform(matrix)
    H = model.components_
    Reconstructed_matrix = model.inverse_transform(W)

    r_squared = r2_score(matrix.flatten(), Reconstructed_matrix.flatten())
    print("err: ", 1 - (model.reconstruction_err_ / total_energy))
    print("VAF: ", 1 - (np.sum(matrix - Reconstructed_matrix)**2)/ np.sum(matrix**2))
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

