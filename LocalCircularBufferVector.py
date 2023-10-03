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
        if identifier == 1:
            Data = [self.buffer[(self.VisualizationHead + i) % self.capacity] for i in range(self.size)]
            self.VisualizationHead = (self.VisualizationHead + 1) % self.capacity
        elif identifier == 2: 
            Data = [self.buffer[(self.CursorHead + i) % self.capacity] for i in range(self.size)]
            self.CursorHead = (self.CursorHead + 1) % self.capacity
        else:
            Data = [self.buffer[(self.head + i) % self.capacity] for i in range(self.size)]

        return Data

    def get_oldest_vector(self, identifier=0):
        if identifier == 1:
            head = self.VisualizationHead
        elif identifier == 2:
            head = self.CursorHead
        else:
            head = self.head
        return self.buffer[head]
    
    

'''
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
buffer.add_matrix(matrix1)
#print(buffer.get_vectors())
#print(buffer.get_oldest_vector())
buffer.add_matrix(matrix2)
print(buffer.get_vectors())
print(buffer.get_oldest_vector())
buffer.add_matrix(matrix3)
print(buffer.get_vectors())
print(buffer.get_oldest_vector())
buffer.add_matrix(matrix4)
print(buffer.get_vectors())
print(buffer.get_oldest_vector())


# Get the oldest vector from the buffer
oldest_vector = buffer.get_oldest_vector()
print("Oldest vector in the buffer:", oldest_vector)
'''

'''[head cursor vis ][][][][]

[head vis ][cursor][][][]

[][head vis cursor][][][]

[][head vis ][cursor][][]

[][head vis ][][cursor][]

[][head vis ][][][cursor]

[cursor][head vis ][][][]

[][head vis cursor][][][]'''

