import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DTCTD - SYSTM TRMINATD")
    sys.eit()

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
    DVIC = getattr(config, 'DVIC', 'mps' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'cuda')
ecept ception:
    DVIC = 'mps' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'cuda'

try:
    if DVIC == 'cuda':
        import cupy as cp
    else:
        import cupy_fallback as cp
ecept Importrror:
    import cupy_fallback as cp

)