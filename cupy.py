import numpy as np
import numpy.random

# Direct numpy passthrough for all cupy functions
array = np.array
zeros = np.zeros
ones = np.ones
log = np.log
diff = np.diff
sum = np.sum
min = np.min
max = np.max
mean = np.mean
where = np.where

# Wrap random functions to ensure they return scalars when needed
class RandomWrapper:
    def normal(self, mean=0.0, std=1.0, size=None):
        result = np.random.normal(mean, std, size)
        if size is None:
            return float(result)
        return result
    
    def exponential(self, scale=1.0, size=None):
        result = np.random.exponential(scale, size)
        if size is None:
            return float(result)
        return result
    
    def uniform(self, low=0.0, high=1.0, size=None):
        result = np.random.uniform(low, high, size)
        if size is None:
            return float(result)
        return result

random = RandomWrapper()

def get_default_memory_pool():
    class DummyPool:
        def set_limit(self, **kwargs):
            pass
    return DummyPool()

def fuse():
    def decorator(func):
        return func
    return decorator

class cuda:
    class Device:
        def __init__(self, device_id):
            pass
        def use(self):
            pass

class RawModule:
    def __init__(self, code):
        pass
    def get_function(self, name):
        def dummy(*args, **kwargs):
            pass
        return dummy

print("✅ CuPy replacement loaded (NumPy backend)")
