class CircularBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.size = 0
        self.head = 0

    def add_point(self, point):
        if self.size < self.capacity:
            self.buffer[(self.head + self.size) % self.capacity] = point
            self.size += 1
        else:
            self.buffer[self.head] = point
            self.head = (self.head + 1) % self.capacity

    def get_points(self):
        return [self.buffer[(self.head + i) % self.capacity] for i in range(self.size)]
    
    def get_oldest_point(self):
        if self.size < self.capacity:  
            return self.buffer[0]
        else:
            return self.buffer[self.head]

# Usage example
# uncomment the code below
buffer = CircularBuffer(5)

# Add points
for i in range(1):  # Adding more than capacity
    buffer.add_point(extend([[i,i],[i,i],[i,i]]))

# Get the points
points = buffer.get_points()
#points=buffer.get_oldest_point()
print(points)



