import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit(1)

import time
import logging
import json
import threading
from typing import Dict, List
from collections import deque
import requests
import websocket

try:
    import config
    DEVICE = getattr(config, 'DEVICE', 'mps' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'cuda')
except Exception:
    DEVICE = 'mps' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'cuda'

try:
    if DEVICE == 'cuda':
        import cupy as cp
    else:
        import cupy_fallback as cp
except ImportError:
    import cupy_fallback as cp

)