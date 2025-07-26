#!/usr/bin/env python3
"""
Fix Configuration for Tests - Ensure paper trading mode
"""
import os
import sys

def setup_test_environment():
    """Set environment variables for testing"""
    # Force paper trading mode
    os.environ["MODE"] = "paper"
    
    # Set minimal required environment variables for testing
    if not os.getenv("OKX_API_KEY"):
        os.environ["OKX_API_KEY"] = "test_key"
    if not os.getenv("OKX_SECRET_KEY"):
        os.environ["OKX_SECRET_KEY"] = "test_secret"
    if not os.getenv("OKX_PASSPHRASE"):
        os.environ["OKX_PASSPHRASE"] = "test_passphrase"
    if not os.getenv("DISCORD_WEBHOOK_URL"):
        os.environ["DISCORD_WEBHOOK_URL"] = "https://discord.com/api/webhooks/test"
    
    print("🔧 Test environment configured:")
    print(f"   MODE: {os.getenv('MODE')}")
    print("   ✅ Required environment variables set")

if __name__ == "__main__":
    setup_test_environment()
    
    # Import and run the specified test
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        print(f"🧪 Running {test_file} with fixed configuration...")
        
        # Import the test module and run it
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
    else:
        print("Usage: python fix_config_for_tests.py <test_file.py>")