import sys
import importlib

# Install import hook for cupy
class CupyImportHook:
    def find_spec(self, name, path, target=None):
        if name == 'cupy':
            # Redirect cupy imports to our fallback
            import cupy_fallback
            sys.modules['cupy'] = cupy_fallback
            return None
        return None

# Install the hook
if 'cupy' not in sys.modules:
    hook = CupyImportHook()
    sys.meta_path.insert(0, hook)

print("✅ CuPy import hook installed")
