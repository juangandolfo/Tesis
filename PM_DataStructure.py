import LocalCircularBufferVector as Buffer
from threading import Semaphore

BufferSize = 1000
NumberChannels = 2 
circular_stack = Buffer.CircularBufferVector(BufferSize, NumberChannels)

stack_lock = Semaphore(1)  # Semaphore for stack access