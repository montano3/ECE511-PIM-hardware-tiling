import numpy as np
import time

A = np.random.rand(2000, 2000)
B = np.random.rand(2000, 2000)

start = time.time()

C = A @ B

end = time.time()

print("Time taken in seconds:", end - start)