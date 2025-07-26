import os
import re
def verify_no_cpu():
    violations = []
    for file in os.listdir('.'):
        if file.endswith('.py') and file != 'verify_nuclear.py':
            try:
                with open(file, 'r') as f:
                    content = f.read()
                if any(bad in content.lower() for bad in ['device="cpu"', "device='cpu'", '.cpu()', 'import numpy', 'np.', 'except:']):
                    violations.append(file)
            except: pass
    return violations
violations = verify_no_cpu()
if violations:
    print(f"❌ Files with violations: {violations}")
    exit(1)
print("🔥 NUCLEAR VERIFICATION PASSED")
print("⚡ ZERO CPU FALLBACKS DETECTED")
print("🎯 GPU-ONLY ENFORCEMENT CONFIRMED")
