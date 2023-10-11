import numpy as np

class CircularBufferVector:
    def __init__(self, capacity, num_cols):
        self.capacity = capacity
        self.num_cols = num_cols
        self.buffer = [[None] * num_cols for _ in range(capacity)]
        self.size = 0
        self.head = 0
        self.VisualizationHead = 0
        self.VisualizationEmpty = True
        self.CursorHead = 0
        self.CursorEmpty = True



    def add_matrix(self, matrix):
        for row in matrix:
            if np.size(np.array(row))==self.num_cols:
                self.add_vector(row)
            else:
                print("error")

    def add_vector(self, vector):
        if self.size < self.capacity:
            self.buffer[(self.head + self.size) % self.capacity] = vector
            self.size += 1
        else:
            self.buffer[self.head] = vector
            if self.head == self.CursorHead and self.CursorEmpty == False:
                self.CursorHead = (self.CursorHead + 1) % self.capacity
            if self.head == self.VisualizationHead and self.VisualizationEmpty == False:
                self.VisualizationHead = (self.VisualizationHead + 1) % self.capacity
            self.head = (self.head + 1) % self.capacity
        
        self.VisualizationEmpty = False
        self.CursorEmpty = False       

    def get_vectors(self, identifier=0):
        Data = []
        if identifier == 1:
            while (self.VisualizationEmpty == False):    
                if self.size < self.capacity:       
                    Data.append(self.buffer[self.VisualizationHead])
                    self.VisualizationHead = (self.VisualizationHead + 1) % self.capacity
                    if self.VisualizationHead == self.size:
                        self.VisualizationEmpty = True
                else:
                    Data.append(self.buffer[self.VisualizationHead])
                    self.VisualizationHead = (self.VisualizationHead + 1) % self.capacity
                    if self.VisualizationHead == self.head:
                        self.VisualizationEmpty = True
        elif identifier == 2:
            while (self.CursorEmpty == False):           
                if self.size < self.capacity:
                    Data.append(self.buffer[self.CursorHead])
                    self.CursorHead = (self.CursorHead + 1) % self.capacity
                    if self.CursorHead == self.size:
                        self.CursorEmpty = True
                else:
                    Data.append(self.buffer[self.CursorHead])
                    self.CursorHead = (self.CursorHead + 1) % self.capacity
                    if self.CursorHead == self.head:
                        self.CursorEmpty = True
        else:
            Data = [self.buffer[(self.head + i) % self.capacity] for i in range(self.size)]

        return Data

    def get_oldest_vector(self, identifier=0):
        Data = []
        if identifier == 1:
            if self.size < self.capacity:
                if self.VisualizationEmpty == False:
                    Data = self.buffer[self.VisualizationHead]
                    self.VisualizationHead = (self.VisualizationHead + 1) % self.capacity
                    if self.VisualizationHead  == self.size:
                        self.VisualizationEmpty = True
            else:
                 if self.VisualizationEmpty == False:
                    Data = self.buffer[self.VisualizationHead]
                    self.VisualizationHead = (self.VisualizationHead + 1) % self.capacity
                    if self.VisualizationHead  == self.head:
                        self.VisualizationEmpty = True
                                    

        elif identifier == 2:
             if self.size < self.capacity:
                if self.CursorEmpty == False:
                    Data = self.buffer[self.CursorHead]
                    self.CursorHead = (self.CursorHead + 1) % self.capacity
                    if self.CursorHead  == self.size:
                        self.CursorEmpty = True
             else: 
                if self.CursorEmpty == False:
                    Data = self.buffer[self.CursorHead]
                    self.CursorHead = (self.CursorHead + 1) % self.capacity
                    if self.CursorHead  == self.head:
                        self.CursorEmpty = True
                             

        else:
            Data = self.buffer[self.head]
        return Data
    
    

# Create a CircularBuffer with a capacity of 3, assuming each matrix has 2 rows and 3 columns
buffer = CircularBufferVector(4, 3)

# Example matrices (each matrix has 2 rows and 3 columns)
matrix1 = [[1, 2, 3], [4, 5, 6]]
matrix2 = [[7, 8, 9], [10, 11, 12,5]]
matrix3 = [[13, 14, 15], [16, 17, 18]]
matrix4 = [[19,20,21],[22,23,24],[25,26,27]]

# Add matrices to the circular buffer
#print(buffer.get_vectors())
#print(buffer.get_oldest_vector())
#buffer.add_matrix(matrix1)
#buffer.add_matrix(matrix2)
buffer.add_matrix(matrix4)
print(buffer.get_vectors())

#print(buffer.get_oldest_vector(1))
#print(buffer.get_oldest_vector(1))
print(buffer.get_vectors(1))
print(buffer.get_oldest_vector(2))
print(buffer.get_oldest_vector(2))
print(buffer.get_oldest_vector(2))
print(buffer.get_oldest_vector(2))
print(buffer.get_vectors(2))
#print(buffer.get_vectors(1))
