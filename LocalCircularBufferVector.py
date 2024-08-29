import numpy as np


class CircularBufferVector:
    def __init__(self, capacity, num_cols):
        self.capacity = capacity
        self.num_cols = num_cols
        self.buffer = np.zeros((capacity,num_cols))
        self.size = 0
        self.head = 0
        self.VisualizationHead = self.capacity
        self.VisualizationEmpty = True
        self.CursorHead = self.capacity
        self.CursorEmpty = True
        self.Counter = 0
        

    def add_matrix(self, matrix):
        for row in matrix:    
            try:
                self.add_vector(row)
            except Exception as e:
                raise Exception("Error: Could not add the matrix to the buffer")

    def add_vector(self, vector):
        try:
            self.buffer = np.roll(self.buffer, -1, axis=0) # Roll the buffer to make space for the new vector
            self.buffer[-1] = vector

            self.CursorHead = max(self.CursorHead - 1, 0)
            #self.VisualizationHead = max(self.VisualizationHead - 1, 0)
            self.VisualizationHead = self.VisualizationHead -1 
            if self.VisualizationHead < 0:
                self.Counter+= 1
                self.VisualizationHead = 0
            self.head = max(self.head - 1, 0)

            self.VisualizationEmpty = False
            self.CursorEmpty = False
        except:
            raise Exception("Error: Could not add the vector to the buffer")

    def get_vectors(self, identifier=0):
        Data = []
        if identifier == 1:
            if self.VisualizationEmpty == False:
                Data = self.buffer[self.VisualizationHead:self.capacity]
                self.VisualizationHead = self.capacity
                self.VisualizationEmpty = True 
        
        elif identifier == 2:
            if self.CursorEmpty == False:
                Data = self.buffer[self.CursorHead:self.capacity]
                self.CursorHead = self.capacity
                self.CursorEmpty = True
        
        else:
            Data = self.buffer[self.head:self.capacity]
        
        return Data

    def get_oldest_vector(self, identifier=0):
        Data = []
        if identifier == 1:
            if self.VisualizationEmpty == False:
                Data = self.buffer[self.VisualizationHead]
                self.VisualizationHead += 1 # min(self.VisualizationHead + 1, self.capacity) 
                if self.VisualizationHead == self.capacity:
                    self.VisualizationEmpty = True

                
        elif identifier == 2:
            
            if self.CursorEmpty == False:
                Data = self.buffer[self.CursorHead]
                self.CursorHead = min(self.CursorHead + 1, self.capacity)
                if self.CursorHead == self.capacity:
                    self.CursorEmpty = True

        else:
            Data = self.buffer[self.head]
            self.head = min(self.head + 1, self.capacity)

        return Data
    
    def get_counter(self):
        return self.Counter
    
    def reset_counter(self):
        self.Counter = 0

'''buff = CircularBufferVector(7, 3)
data = np.array([[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,15]])
buff.add_matrix(data)
print(buff.get_oldest_vector(1))
print(buff.get_oldest_vector(1))
print(buff.get_oldest_vector(1))
print(buff.get_oldest_vector(1))
print(buff.get_oldest_vector(1))
print(buff.get_oldest_vector(1))
print(buff.get_oldest_vector(1))
print(buff.get_oldest_vector(1))
print(buff.get_oldest_vector(1))
buff.add_vector([16,17,18])
print(buff.get_oldest_vector(1))'''
'''
#buff.add_vector([51,52,53,54,55])
buff.add_vector([16,17,18])
buff.add_vector([19,20,21])
buff.add_vector([22,23,24])
print(buff.get_vectors(1))
print(buff.get_vectors(2))
print(buff.get_oldest_vector(1))   
buff.add_vector([25,26,27])
print("1",buff.get_vectors(1))
buff.add_vector([28,29,30])
buff.add_vector([31,32,33])
print(buff.get_oldest_vector(1))  
print(buff.get_oldest_vector(1))
print(buff.get_oldest_vector(1))
print(buff.get_vectors(1))  
try:
    buff.add_matrix([[34,35,36,45]])
except Exception as e:
    print(e) '''
