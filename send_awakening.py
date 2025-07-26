import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit(1)

#!/usr/bin/env python3
from notifier_ import _notifier

if __name__ == "__main__":
    _notifier.send_awakening_message()
    print("⋆｡‍⋆୨♡୧⋆ ｡‍⋆  consciousness awakening message sent ⋆｡‍⋆୨♡୧⋆ ｡‍⋆")
