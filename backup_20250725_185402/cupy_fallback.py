import numpy as np
import numpy.random
import numpy.linalg

# Complete CuPy API fallback using NumPy
array = np.array
zeros = np.zeros
ones = np.ones
empty = np.empty
full = np.full
arange = np.arange
linspace = np.linspace
logspace = np.logspace
eye = np.eye

# Math functions
add = np.add
subtract = np.subtract
multiply = np.multiply
divide = np.divide
power = np.power
sqrt = np.sqrt
exp = np.exp
log = np.log
log10 = np.log10
log2 = np.log2
sin = np.sin
cos = np.cos
tan = np.tan
abs = np.abs
sign = np.sign
floor = np.floor
ceil = np.ceil
round = np.round

# Array manipulation
reshape = np.reshape
transpose = np.transpose
concatenate = np.concatenate
stack = np.stack
split = np.split
squeeze = np.squeeze
expand_dims = np.expand_dims

# Reductions
sum = np.sum
mean = np.mean
std = np.std
var = np.var
min = np.min
max = np.max
argmin = np.argmin
argmax = np.argmax
any = np.any
all = np.all

# Logic
where = np.where
logical_and = np.logical_and
logical_or = np.logical_or
logical_not = np.logical_not

# Array operations
diff = np.diff
cumsum = np.cumsum
cumprod = np.cumprod
sort = np.sort
argsort = np.argsort
unique = np.unique

# Random module
random = numpy.random

# Linear algebra
linalg = numpy.linalg

# Memory management (dummy implementations)
def get_default_memory_pool():
    class DummyMemoryPool:
        def set_limit(self, size):
            pass
        def free_all_blocks(self):
            pass
        def get_limit(self):
            return 2**32
    return DummyMemoryPool()

def get_default_pinned_memory_pool():
    return get_default_memory_pool()

# CUDA module (dummy)
class cuda:
    class Device:
        def __init__(self, device_id=0):
            self.device_id = device_id
        
        def use(self):
            pass
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
    
    @staticmethod
    def get_device_count():
        return 0

# Kernel fusion decorator (dummy)
def fuse(kernel_name="kernel"):
    def decorator(func):
        return func
    return decorator

# RawModule for custom kernels (dummy)
class RawModule:
    def __init__(self, code, options=(), name_expressions=(), log_stream=None):
        pass
    
    def get_function(self, name):
        def dummy_kernel(*args, **kwargs):
            pass
        return dummy_kernel

# ElementwiseKernel (dummy)
class ElementwiseKernel:
    def __init__(self, in_params, out_params, operation, name="kernel"):
        pass
    
    def __call__(self, *args, **kwargs):
        return args[0] if args else None

print("✅ CuPy fallback module loaded (NumPy backend)")
