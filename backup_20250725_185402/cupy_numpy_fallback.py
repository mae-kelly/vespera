import numpy as np
import numpy.random

# Complete CuPy replacement using NumPy
array = np.array
zeros = np.zeros
ones = np.ones
log = np.log
diff = np.diff
sum = np.sum
min = np.min
max = np.max
mean = np.mean
std = np.std
sqrt = np.sqrt
exp = np.exp
abs = np.abs
where = np.where
all = np.all
any = np.any
concatenate = np.concatenate

# Random module
random = numpy.random

def get_default_memory_pool():
    class DummyPool:
        def set_limit(self, **kwargs):
            pass
    return DummyPool()

def get_default_pinned_memory_pool():
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

# Print confirmation
print("✅ NumPy-based CuPy fallback loaded")
