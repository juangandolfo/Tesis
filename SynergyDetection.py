from sklearn.decomposition import NMF
import sklearn.metrics as skm
import numpy as np
import csv
import itertools
import matplotlib.pyplot as plt
import GlobalParameters
import kneed

def plot_bars(H, s, m):
    # Ensure that H and Model_H have the same shape

    for i in range(s):
        # Create a new figure for each row
        plt.figure()

        # Create a subplot for the H matrix
        plt.subplot(111)
        plt.bar(range(m), H[i, :])
        plt.title(f'H Matrix - Row {i+1}')

    # Show the plot
    plt.show()
    return

def ReadCSV(csv_file):
    with open(csv_file, 'r') as file:
        #create a matrix of 8 columns and 1 row
        matrix = np.matrix([[0,0,0,0,0,0,0,0]])

        csv_reader = csv.reader(file, delimiter=';')
        # Skip the headers row
        next(csv_reader)
        # Read each row of csv file
        for row in csv_reader:
            row = np.array(row, dtype=np.float64)  # Convert the row to numpy array
            matrix = np.vstack([matrix, row[1:9]]) # Add the row to a matrix

    return matrix

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
        #print("processing synergy detection")
        #nndsvd is the initialization method that returns  a matrix with the largest dispersion.
        #cd is the solver used because is compatible with nndsvd
        model = NMF(n_components=n_components, init='nndsvd', tol= 1e-5,max_iter=20000, solver='cd')
        #model = NMF(n_components=n_components, init='random', tol= 1e-5, max_iter=200000, solver='mu')
        #print("Fitting model with ", n_components, " components")
        W = model.fit_transform(matrix)

        #H.append(model.components_)
        H = np.matrix(model.components_)

        #H_Max = np.max(H[n_components-2])
        #H_Normalized.append(H[n_components-2] / H_Max)
        Reconstructed_matrix = model.inverse_transform(W)

        # pseudo inverse matrix of H
        #numpy_H_pinv.append(np.linalg.pinv(H_Normalized[n_components-2]))

        r_squared = skm.r2_score(np.asarray(matrix), np.asarray(Reconstructed_matrix) )

        # i want to calculate the VAF
        # the vaf is calculated as the sum of the squares of the difference between the original matrix and the reconstructed matrix for each element
        vaf = 1 - (np.sum((matrix - Reconstructed_matrix) ** 2) / np.sum(matrix ** 2))
        #print("VAF: ", vaf)
        vafs.append(vaf)
        H_inv = np.linalg.pinv(H)
        models.append((n_components, H, H_inv, r_squared, vaf))
        # Comparación directa de VAFs
        if n_components == 2:
            output = (n_components, H, H_inv,r_squared, vafs)
        else:
            #print(vaf, vafs[-2])
            if vaf>vafs[-2]:
                output = (n_components, H, H_inv, r_squared, vafs)
        '''if n_components ==2:
            output = (n_components, H, r_squared, vafs)
        else:
            #print(vaf, vafs[-2])
            if vaf>0.9 and outputDefined==False:
                output = (n_components, H, r_squared, vafs)
                outputDefined = True'''
        

    #deteccion de codo
    ''' x = range(2, GlobalParameters.MusclesNumber+1)
    y = vafs

    # calculate and show knee/elbow
    kneedle = kneed.KneeLocator(x,y,curve='concave',direction='increasing')
    knee_point = kneedle.knee
    print('Knee: ', knee_point)
    if knee_point == None:
        knee_point = 2
        print('Knee: None')
    print('Knee: ', knee_point)
    output = models[knee_point-2]'''

    #return output, vafs
    return models, vafs, output

def BarsGraphic(n, H, R2, vafs):
    aux= []
    plt.figure()
    plt.subplot(111)
    plt.plot(range(2,9), vafs)
    plt.figure()

    for j in range(0, n):
        plt.subplot(100*n+10+j+1)
        for i in range(0, H.shape[1]):
            aux.append(np.max(H[j,i]))
        plt.bar(range(0,8), aux)
        aux = []

    plt.show()

def execute():
    # create a matrix from a csv file
    matrix = np.matrix([[0,0,0,0,0,0,0,0]])
    #csv_file = './prueba1Modificada.csv'
    csv_file = './prueba1.csv'
    # Example matrix to factorize
    # i will create a matrix of 25x8 with float numbers between 1 and 2
    #matrix = np.random.rand(10000, 8)
    total_energy = np.linalg.norm(matrix, 'fro',)+1

    # Read a csv file with the data
    #matrix = ReadCSV(csv_file)

    class model:
        n = 0
        H = []
        Hinv = []
        R2 = 0
        vaf = 0
        W = []

    Model = model()

    cantidadDeDatos = 10000
    numeroDeSinergias = 4
    numeroDeMusculos = 8

    # Create a random matrix with high dispersion
    W = np.random.rand(cantidadDeDatos,numeroDeSinergias)
    W = np.maximum(W, 0)
    print ("W: ", W)
    '''#H = np.random.rand(numeroDeSinergias,numeroDeMusculos)

    H = np.maximum(H, 0)
    print ("H: ", H)
    for i in range(H.shape[0]):
        H[i,i] = 0
    '''
    H = np.array([[1,0,0,0,0,0,0,0],[0,1,0,0,0,0,0,0],[0,0,1,0,0,0,0,0],[0,0,0,1,0,0,0,0]])
    M = np.dot(W,H)

    aux= []
    Model.n, Model.H, Model.R2, vafs = calculateSynergy(M)
    print(vafs)

    BarsGraphic(Model.n, Model.H, Model.R2, vafs)
    '''plt.figure()
    plt.subplot(111)
    plt.plot(range(2,9), vafs)
    plt.figure()

    for j in range(0, Model.n):
        plt.subplot(100*Model.n+10+j+1)
        for i in range(0, Model.H.shape[1]):
            aux.append(np.max(Model.H[j,i]))
        plt.bar(range(0,8), aux)
        aux = []
    plt.figure()
    for j in range(0, numeroDeSinergias):
        plt.subplot(100*numeroDeSinergias+10+j+1)
        for i in range(0, H.shape[1]):
            aux.append(np.max(H[j,i]))
        plt.bar(range(0,8), aux)
        aux = []
    plt.show()'''

    #for i in range(model.n):
    #    plt.plot(range(0,8), model.H[i,:])

    x = [2,3,4,5,6,7,8]
    y = vafs


    # calculate and show knee/elbow
    kneedle = kneed.KneeLocator(x,y,curve='concave',direction='increasing')
    knee_point = kneedle.knee
    print('Knee: ', knee_point)

    # Plot VAF data
    x = list(range(2, 9))  # Number of synergies
    plt.plot(x, vafs, marker='o', label='VAF Curve')
    plt.xlabel('Number of Synergies')
    plt.ylabel('VAF')
    plt.title('VAF vs Number of Synergies')

    # Plot knee point
    plt.axvline(x=knee_point, color='red', linestyle='--', label='Knee Point')
    plt.legend()

    # Annotate knee point
    plt.text(knee_point + 0.1, max(vafs) - 0.05, f'Knee Point: {knee_point}', color='red')

    # Show plot
    plt.show()


    print("original model: ", numeroDeSinergias, "\n", H, "\n", Model.R2, "\n", Model.vaf)
    print ("Best number of components: ", Model.n, "\n", Model.H,"\n", Model.R2,"\n", Model.vaf)
    #plot_bars(H, H.shape[0], H.shape[1])

    #plot_bars(Model.H, Model.H.shape[0], Model.H.shape[1])

    print("H: ", H)



    #i will calculate the correlation between the original matrix and the reconstructed matrix
    #for this i will permutate in all posible combinations the rows of the reconstructed matrix and calculate the correlation
    #using np.corrcoef function
    # Calculate correlation between original matrix and reconstructed matrix
    correlations = []
    vaf = 0
    rsquared =0
    a = np.sum(H ** 2)
    for permutation in itertools.permutations(Model.H):
        vaf = max(vaf, 1 - (np.sum((H - (np.asarray(permutation))) ** 2) / a))
        rsquared = max(rsquared,skm.r2_score(H.flatten(), np.asarray(permutation).flatten()))
        permuted_matrix = np.dot(np.asarray(permutation), H.T)
        correlation = np.corrcoef(np.asarray(permutation).flatten(), H.flatten())[0,1]
        correlations.append(correlation)

    max_correlation = max(correlations)

    print("Max correlation:", max_correlation)

    #normalizo por musculos
    print("H: ", H)
    for i in range(H.shape[1]):
        H[:,i] = H[:,i] / np.max(H[:,i])
    for i in range(Model.H.shape[1]):
        Model.H[:,i] = Model.H[:,i] / np.max(Model.H[:,i])

    # normalizo por sinergias
    for i in range(H.shape[0]):
        H[i,:] = H[i,:] / np.linalg.norm(H[i,:])
    for i in range(Model.H.shape[0]):
        Model.H[i,:] = Model.H[i,:] / np.linalg.norm(Model.H[i,:])

    max_corr = 0
    #iterar cambiando orden de vecotr
    vector = np.asarray(range(Model.n))

    for permutations in itertools.permutations(vector):
        producto_punto = np.dot(Model.H[permutations,:], H.T)
        if np.trace(producto_punto)/Model.n > max_corr:
            best_permutation = permutations
            max_corr = np.trace(producto_punto)/Model.n
            print("Permutation: ", permutations)
            print("Producto punto: ", producto_punto)
        #max_corr = max(max_corr, np.trace(producto_punto)/Model.n)

    print("Max correlation: ", max_corr)

    Model.H = Model.H[best_permutation,:]

    Model.Hinv = np.linalg.pinv(Model.H)

    W_rec = np.dot(M, Model.Hinv)
    count = 0
    print ("W_rec: ", W_rec.shape)
    #for row in W_rec:
    #    if np.min(row) < 0:
    #        count += 1
    #        print("count :", count, "min: ", np.min(row), "max: ", np.max(row), "ratio: ", np.min(row)/np.max(row))


    #product = np.dot(Model.H, H.T)
    #traza = np.trace(product)


    # VAF en funcion de numeros de sinergias
    #print("product: ", product)
    #print("traza: ", traza)
    #print("Model.n : ", Model.n)
    #print("model.H: ", Model.H)
    #print("H: ", H)





    '''with open(csv_file, 'r') as file:
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
    '''
    # Specify the number of components (factors) for factorization
    #matrix = np.asarray(np.abs(matrix))

    #print(csv_file, " has been read successfully")

    '''H = []
    numpy_H_pinv = []
    H_Normalized = []
    # Perform NMF
    for n_components in range(2, 9):
        print("\n\nNumber of components: ", n_components)
        #nndsvd is the initialization method that returns  a matrix with the largest dispersion.
        #cd is the solver used because is compatible with nndsvd
        model = NMF(n_components=n_components, init='nndsvd', tol= 1e-5,max_iter=2000, solver='cd')
        W = model.fit_transform(matrix)
        #model.fit(matrix)

        H.append(model.components_)
        H_Max = np.max(H[n_components-2])
        H_Normalized.append(H[n_components-2] / H_Max)
        #Reconstructed_matrix = model.inverse_transform(W)
        # pseudo inverse matrix of H
        numpy_H_pinv.append(np.linalg.pinv(H_Normalized[n_components-2]))
        #print("Pseudo inverse of H: ", numpy_H_pinv)

        #print(matrix.shape, Reconstructed_matrix.shape)

        #r_squared = skm.r2_score( np.asarray(matrix), np.asarray(Reconstructed_matrix) )
        #print("R^2: ", r_squared)

        #print("err: ", 1 - (model.reconstruction_err_ / total_energy))
        vaf = 0
        # i want to calculate the VAF
        # the vaf is calculated as the sum of the squares of the difference between the original matrix and the reconstructed matrix for each element
        #vaf = 1 - (np.sum((matrix - Reconstructed_matrix) ** 2) / np.sum(matrix ** 2))
        print("VAF: ", vaf)


        # Print the factorized matrices
        #print("Matrix W (Basis Vectors):")
        #print(W)
        print("\nMatrix H (Coefficients):")
        print(H_Normalized)'''


    #n, H,HInv, r2, vaf = calculateSynergy(matrix)
    #print ("Best number of components: ", n, "\n", H,"\n", HInv,"\n", r2,"\n", vaf)

    '''csv_file = './prueba1Modificada.csv'
    matrix = np.matrix([[0,0,0,0,0,0,0,0]])

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



    previous_shape = (0,0)
    for i in range(0, len(numpy_H_pinv)):
        print("pseudo inverse of H: ", numpy_H_pinv[i])

        SynergyActivations = np.dot(np.abs(matrix),numpy_H_pinv[i])
        for j in range(0, SynergyActivations.shape[0], 1000):
            if max(SynergyActivations[j]).any() > 0.005:
                print("Result for row", j, ":", SynergyActivations[j])

    #print("\Calculated Matrix:")
    #print(Calculated_matrix)
    '''



    # Las sinergias elegidas deben tener al menos un 0 en lugares distintos para garantizar que haya una unica solucion.
    # Revisar VAFS
    # Encontrar un codo y dar la opcion de mostrar
    # Venir a la proxima reunion con un control a partir de eleccion de sinergias arbitrarias

#execute()