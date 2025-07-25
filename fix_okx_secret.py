#!/usr/bin/env python3
import base64
import os

def fix_okx_secret():
    """Fix OKX secret key encoding"""
    secret = os.getenv('OKX_SECRET_KEY', '')
    
    if not secret:
        print("❌ No OKX_SECRET_KEY found in environment")
        return False
    
    print(f"Current secret: {secret[:10]}...")
    
    # Check if it's already base64 encoded
    try:
        decoded = base64.b64decode(secret)
        print("✅ Secret appears to be valid base64")
        return True
    except:
        print("⚠️ Secret is not base64 encoded")
        
        # Try to base64 encode it
        try:
            encoded = base64.b64encode(secret.encode()).decode()
            print(f"🔧 Base64 encoded version: {encoded}")
            print("💡 Try updating your .env with:")
            print(f"OKX_SECRET_KEY={encoded}")
            return False
        except Exception as e:
            print(f"❌ Could not encode secret: {e}")
            return False

if __name__ == "__main__":
    fix_okx_secret()
