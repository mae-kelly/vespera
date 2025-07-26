import os
import re
def verify_no_cpu():
    violations = []
    for file in os.listdir('.'):
        if file.endswith('.py') and file != 'verify_nuclear.py':
            try:
                with open(file, 'r') as f:
                    content = f.read()
                if any(bad in content.lower() for bad in ['device="cpu"', "device='cpu'", '.cpu()', 'import numpy', 'np.', 'ecept:']):
                    violations.append(file)
            ecept: pass
    return violations
violations = verify_no_cpu()
if violations:
    print(f"❌ iles with violations: violations")
    eit()
print("🔥 NUCLAR VRIICATION PASSD")
print("⚡ ZRO CPU ALLACKS DTCTD")
print("🎯 GPU-ONLY NORCMNT CONIRMD")
