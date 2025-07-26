#!/usr/bin/env python3
"""
Production HFT System Validator - Check for fallback violations
"""

import os
import ast
import sys
import subprocess
from pathlib import Path

class ProductionValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.project_root = Path.cwd()
        
        # Forbidden patterns that indicate fallback mechanisms
        self.forbidden_patterns = [
            ('fallback', 'Fallback mechanisms BANNED'),
            ('mock', 'Mock data BANNED'),
            ('simulation', 'Simulation BANNED'),
            ('demo', 'Demo mode BANNED'),
            ('test_mode', 'Test mode BANNED'),
            ('dry_run', 'Dry run BANNED'),
            ('or 0.0', 'Default 0.0 values BANNED'),
            ('or []', 'Empty fallbacks BANNED'), 
            ('or None', 'None fallbacks BANNED'),
            ('unwrap_or', 'Unwrap fallbacks BANNED'),
            ('get("confidence", 0)', 'Confidence fallbacks BANNED'),
            ('except:', 'Bare except BANNED'),
            ('return 0.0', 'Zero returns BANNED'),
            ('return []', 'Empty returns BANNED'),
            ('return None', 'None returns BANNED'),
        ]
    
    def scan_file_for_violations(self, filepath: Path):
        """Scan file for forbidden patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                line_clean = line.strip().lower()
                
                # Skip comments and empty lines
                if not line_clean or line_clean.startswith('#'):
                    continue
                
                for pattern, message in self.forbidden_patterns:
                    if pattern.lower() in line_clean:
                        # Check for valid exceptions
                        if self._is_valid_exception(pattern, line, filepath):
                            continue
                        
                        self.errors.append(f"🚫 {filepath}:{line_num} - {message}")
                        self.errors.append(f"   >>> {line.strip()}")
                        
        except Exception as e:
            self.errors.append(f"❌ Error reading {filepath}: {e}")
    
    def _is_valid_exception(self, pattern, line, filepath):
        """Check if this is a valid exception to the banned pattern"""
        
        # Allow in docstrings
        if '"""' in line or "'''" in line:
            return True
            
        # Allow in comments
        if line.strip().startswith('#'):
            return True
        
        # Allow some mathematical operations
        if pattern == 'or 0.0' and any(x in line for x in ['torch.', 'numpy.', 'math.']):
            return True
            
        # Allow return 0.0 in specific mathematical contexts
        if pattern == 'return 0.0' and any(x in line for x in ['def __len__', 'def count', 'def zero']):
            return True
            
        # Allow return [] for iterators
        if pattern == 'return []' and any(x in line for x in ['def __iter__', 'def keys', 'def values']):
            return True
            
        return False
    
    def validate_python_syntax(self):
        """Check Python syntax"""
        python_files = [f for f in self.project_root.glob("*.py") 
                       if not f.name.startswith('test_')]
        
        syntax_ok = 0
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                ast.parse(content)
                syntax_ok += 1
                print(f"✅ {py_file.name} syntax OK")
            except SyntaxError as e:
                self.errors.append(f"❌ {py_file}: Syntax error at line {e.lineno}: {e.msg}")
            except Exception as e:
                self.errors.append(f"❌ {py_file}: Error parsing: {e}")
        
        print(f"📝 Python syntax check: {syntax_ok}/{len(python_files)} files OK")
    
    def validate_rust_compilation(self):
        """Check Rust compilation"""
        if not Path("Cargo.toml").exists():
            print("📦 No Cargo.toml found - skipping Rust validation")
            return
        
        try:
            result = subprocess.run(['cargo', 'check'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Rust compilation OK")
            else:
                self.errors.append(f"❌ Rust compilation failed:")
                for line in result.stderr.split('\n')[:10]:  # First 10 lines
                    if line.strip():
                        self.errors.append(f"   {line}")
                        
        except subprocess.TimeoutExpired:
            self.errors.append("❌ Rust build timeout")
        except FileNotFoundError:
            self.warnings.append("⚠️ Cargo not found - install Rust to validate")
        except Exception as e:
            self.errors.append(f"❌ Rust validation error: {e}")
    
    def validate_environment(self):
        """Check environment configuration"""
        if not Path(".env").exists():
            self.errors.append("❌ .env file missing")
            return
        
        # Check critical environment variables
        required_vars = ['OKX_API_KEY', 'OKX_SECRET_KEY', 'OKX_PASSPHRASE', 'DISCORD_WEBHOOK_URL']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or 'your_' in value.lower():
                missing_vars.append(var)
        
        if missing_vars:
            self.errors.append(f"❌ Unconfigured environment variables: {missing_vars}")
        else:
            print("✅ Environment variables configured")
        
        # Check mode
        mode = os.getenv('MODE', '').lower()
        if mode != 'live':
            self.errors.append(f"❌ MODE must be 'live', found: '{mode}'")
        else:
            print("✅ MODE set to 'live'")
    
    def validate_gpu(self):
        """Check GPU availability"""
        try:
            import torch
            
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                print(f"✅ CUDA GPU: {gpu_name}")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                print("✅ Apple MPS detected")
                try:
                    test_tensor = torch.zeros(1, device='mps')
                    print("✅ MPS functionality verified")
                except Exception as e:
                    self.errors.append(f"❌ MPS test failed: {e}")
            else:
                self.errors.append("❌ No GPU detected - production requires GPU")
                
        except ImportError:
            self.errors.append("❌ PyTorch not available")
        except Exception as e:
            self.errors.append(f"❌ GPU validation error: {e}")
    
    def test_critical_imports(self):
        """Test critical module imports"""
        critical_modules = ['torch', 'pandas', 'requests', 'websocket']
        
        for module in critical_modules:
            try:
                __import__(module)
                print(f"✅ {module} available")
            except ImportError:
                self.errors.append(f"❌ Missing module: {module}")
    
    def test_production_modules(self):
        """Test production modules load correctly"""
        modules_to_test = ['config', 'signal_engine', 'confidence_scoring']
        
        for module_name in modules_to_test:
            try:
                module = __import__(module_name)
                print(f"✅ {module_name} loads OK")
                
                # Special checks
                if module_name == 'config':
                    if hasattr(module, 'MODE') and module.MODE == 'live':
                        print("✅ Config in live mode")
                    else:
                        self.errors.append("❌ Config not in live mode")
                        
            except ImportError as e:
                self.errors.append(f"❌ Cannot import {module_name}: {e}")
            except Exception as e:
                self.errors.append(f"❌ {module_name} error: {e}")
    
    def run_validation(self):
        """Run complete validation"""
        print("🔥 PRODUCTION SYSTEM VALIDATION")
        print("=" * 50)
        
        # 1. Scan for fallback violations
        print("🔍 Scanning for fallback violations...")
        python_files = [f for f in self.project_root.glob("*.py") 
                       if not f.name.startswith('test_') and f.name != 'production_validator.py']
        
        violation_count = 0
        for py_file in python_files:
            before_count = len(self.errors)
            self.scan_file_for_violations(py_file)
            violations_in_file = len(self.errors) - before_count
            if violations_in_file > 0:
                violation_count += violations_in_file
        
        if violation_count == 0:
            print(f"✅ Scanned {len(python_files)} Python files - NO VIOLATIONS FOUND!")
        else:
            print(f"❌ Found {violation_count} violations in {len(python_files)} Python files")
        
        # Scan Rust files too
        rust_files = list(self.project_root.glob("src/*.rs"))
        if rust_files:
            print(f"🦀 Scanning {len(rust_files)} Rust files...")
            for rust_file in rust_files:
                self.scan_file_for_violations(rust_file)
        
        # 2. Other validations
        print("\n🐍 Validating Python syntax...")
        self.validate_python_syntax()
        
        print("\n🦀 Validating Rust compilation...")
        self.validate_rust_compilation()
        
        print("\n⚙️ Validating environment...")
        self.validate_environment()
        
        print("\n🔥 Validating GPU...")
        self.validate_gpu()
        
        print("\n📦 Testing critical imports...")
        self.test_critical_imports()
        
        print("\n🧪 Testing production modules...")
        self.test_production_modules()
        
        # Final report
        print("\n" + "=" * 50)
        print("🔥 VALIDATION RESULTS")
        print("=" * 50)
        
        if self.errors:
            print(f"❌ CRITICAL ERRORS FOUND: {len(self.errors)}")
            print("\nFirst 20 errors:")
            for i, error in enumerate(self.errors[:20]):
                print(f"   {error}")
            
            if len(self.errors) > 20:
                print(f"   ... and {len(self.errors) - 20} more errors")
            
            print(f"\n🚫 SYSTEM NOT READY FOR PRODUCTION")
            print("   Fix all errors before deploying!")
            return False
        else:
            print("✅ ZERO ERRORS FOUND!")
            print("\n🎉 FALLBACK ELIMINATION: SUCCESS")
            print("   🔴 No fallback mechanisms detected")
            print("   🔴 System will fail fast on invalid data")
            print("   🔴 Production-ready behavior enforced")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if not self.errors:
            print("\n🟢 SYSTEM VALIDATED FOR PRODUCTION")
            print("\n🚀 Ready to start:")
            print("   python3 main.py --mode live")
            print("\n💀 System will crash if live data unavailable!")
            print("   This is CORRECT production behavior.")
            return True
        
        return False

if __name__ == "__main__":
    validator = ProductionValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)
