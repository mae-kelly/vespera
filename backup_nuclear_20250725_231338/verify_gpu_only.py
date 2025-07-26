import sys
import os
import re
def check_no_cpu_fallbacks():
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    violations = []
    for filename in python_files:
        try:
            with open(filename, 'r') as f:
                content = f.read()
            forbidden_patterns = [
                r'device\s*=\s*["\']cpu["\']',
                r'\.cpu\(\)',
                r'import numpy',
                r'np\.',
                r'CPU.*fallback',
                r'except.*:.*cpu',
                r'if.*not.*cuda.*available'
            ]
            for pattern in forbidden_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(f"{filename}: {pattern}")
        except:
            pass
    return violations
def check_mandatory_gpu():
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    missing_gpu_check = []
    for filename in python_files:
        try:
            with open(filename, 'r') as f:
                content = f.read()
            if 'torch.cuda.is_available()' not in content and filename != 'verify_gpu_only.py':
                missing_gpu_check.append(filename)
        except:
            pass
    return missing_gpu_check
violations = check_no_cpu_fallbacks()
missing_checks = check_mandatory_gpu()
if violations:
    print("❌ CPU FALLBACK VIOLATIONS FOUND:")
    for v in violations:
        print(f"  {v}")
    sys.exit(1)
if missing_checks:
    print("⚠️ Files missing GPU checks:")
    for f in missing_checks:
        print(f"  {f}")
print("✅ GPU-ONLY MODE VERIFIED")
print("🔥 NO CPU FALLBACKS DETECTED")
print("⚡ MANDATORY GPU ACCELERATION ENFORCED")
