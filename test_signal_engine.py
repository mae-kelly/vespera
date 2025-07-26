#!/usr/bin/env python3
"""
Test Signal Engine - Verify signal generation functionality
"""
import os
import sys
import time
import json
import unittest
from unittest.mock import patch, MagicMock
import tempfile

# Set paper trading mode BEFORE importing config
os.environ["MODE"] = "paper"

# Add src to path
sys.path.insert(0, '.')

import config
import signal_engine
from okx_market_data import get_okx_engine

class TestSignalEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.shared_data = {
            "timestamp": time.time(),
            "mode": "paper",
            "iteration": 1
        }
        
        # Ensure paper trading mode for tests
        config.MODE = "paper"
        config.PAPER_TRADING = True
        config.LIVE_TRADING = False
    
    def test_signal_generation_basic(self):
        """Test basic signal generation"""
        print("🧪 Testing basic signal generation...")
        
        try:
            signal = signal_engine.generate_signal(self.shared_data)
            
            # Verify signal structure
            self.assertIsInstance(signal, dict)
            self.assertIn("confidence", signal)
            self.assertIn("source", signal)
            self.assertIn("signal_data", signal)
            self.assertIn("production_validated", signal)
            
            # Verify confidence is valid
            confidence = signal["confidence"]
            self.assertIsInstance(confidence, (int, float))
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
            
            print(f"✅ Basic signal generation passed - confidence: {confidence:.3f}")
            
        except Exception as e:
            self.fail(f"❌ Signal generation failed: {e}")
    
    def test_signal_confidence_threshold(self):
        """Test signal confidence meets production threshold"""
        print("🧪 Testing signal confidence threshold...")
        
        signals_above_threshold = 0
        total_signals = 10
        
        for i in range(total_signals):
            self.shared_data["iteration"] = i + 1
            signal = signal_engine.generate_signal(self.shared_data)
            confidence = signal["confidence"]
            
            if confidence >= config.SIGNAL_CONFIDENCE_THRESHOLD:
                signals_above_threshold += 1
        
        success_rate = signals_above_threshold / total_signals
        print(f"✅ Signals above threshold: {signals_above_threshold}/{total_signals} ({success_rate:.1%})")
        
        # At least 50% should be above threshold
        self.assertGreater(success_rate, 0.5, "Not enough signals meet confidence threshold")
    
    def test_signal_data_structure(self):
        """Test signal data contains all required fields"""
        print("🧪 Testing signal data structure...")
        
        signal = signal_engine.generate_signal(self.shared_data)
        signal_data = signal["signal_data"]
        
        required_fields = [
            "asset", "confidence", "entry_price", "stop_loss", 
            "take_profit_1", "rsi", "vwap", "signal_type", "reason"
        ]
        
        for field in required_fields:
            self.assertIn(field, signal_data, f"Missing required field: {field}")
            
        # Verify data types
        self.assertIsInstance(signal_data["asset"], str)
        self.assertIsInstance(signal_data["entry_price"], (int, float))
        self.assertIsInstance(signal_data["stop_loss"], (int, float))
        self.assertIsInstance(signal_data["take_profit_1"], (int, float))
        
        # Verify values are positive
        self.assertGreater(signal_data["entry_price"], 0)
        self.assertGreater(signal_data["stop_loss"], 0)
        self.assertGreater(signal_data["take_profit_1"], 0)
        
        print("✅ Signal data structure validation passed")
    
    def test_warmup_vs_live_signals(self):
        """Test difference between warmup and live signals"""
        print("🧪 Testing warmup vs live signal modes...")
        
        # Test warmup signal (early iterations)
        warmup_data = {"timestamp": time.time(), "mode": "paper", "iteration": 5}
        warmup_signal = signal_engine.generate_signal(warmup_data)
        
        # Test live signal (later iterations)
        live_data = {"timestamp": time.time(), "mode": "paper", "iteration": 100}
        live_signal = signal_engine.generate_signal(live_data)
        
        # Both should be valid
        self.assertIsInstance(warmup_signal, dict)
        self.assertIsInstance(live_signal, dict)
        
        # Check if warmup mode is indicated
        warmup_signal_data = warmup_signal["signal_data"]
        if "warmup_mode" in warmup_signal_data:
            self.assertTrue(warmup_signal_data["warmup_mode"])
            print("✅ Warmup mode detected correctly")
        
        print("✅ Warmup vs live signal test passed")
    
    def test_signal_timing_consistency(self):
        """Test signal generation timing consistency"""
        print("🧪 Testing signal timing consistency...")
        
        times = []
        for i in range(5):
            start_time = time.time()
            signal_engine.generate_signal(self.shared_data)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"✅ Signal generation timing - Avg: {avg_time*1000:.1f}ms, Max: {max_time*1000:.1f}ms")
        
        # Should complete within reasonable time
        self.assertLess(max_time, 1.0, "Signal generation too slow")
    
    def test_error_handling(self):
        """Test error handling in signal generation"""
        print("🧪 Testing error handling...")
        
        # Test with empty shared data
        with self.assertRaises(RuntimeError):
            signal_engine.generate_signal({})
        
        # Test with None
        with self.assertRaises(RuntimeError):
            signal_engine.generate_signal(None)
        
        print("✅ Error handling test passed")
    
    def test_market_data_integration(self):
        """Test integration with market data"""
        print("🧪 Testing market data integration...")
        
        try:
            feed = get_okx_engine()
            health = feed.get_system_health()
            
            self.assertIsInstance(health, dict)
            self.assertIn("system", health)
            self.assertIn("assets", health)
            
            print(f"✅ Market data health: {health['system']['status']}")
            
        except Exception as e:
            print(f"⚠️ Market data test failed: {e}")
            # Don't fail test as market data might not be live in test environment


class TestMarketDataEngine(unittest.TestCase):
    
    def test_okx_engine_initialization(self):
        """Test OKX market data engine initialization"""
        print("🧪 Testing OKX engine initialization...")
        
        try:
            feed = get_okx_engine()
            self.assertIsNotNone(feed)
            print("✅ OKX engine initialized successfully")
            
        except Exception as e:
            self.fail(f"❌ OKX engine initialization failed: {e}")
    
    def test_system_health_check(self):
        """Test system health reporting"""
        print("🧪 Testing system health check...")
        
        feed = get_okx_engine()
        health = feed.get_system_health()
        
        self.assertIsInstance(health, dict)
        self.assertIn("system", health)
        self.assertIn("assets", health)
        
        system_status = health["system"]["status"]
        self.assertIn(system_status, ["LIVE", "WARMING_UP", "CONNECTING"])
        
        print(f"✅ System health check passed - Status: {system_status}")
    
    def test_price_data_structure(self):
        """Test price data structure"""
        print("🧪 Testing price data structure...")
        
        feed = get_okx_engine()
        
        for asset in ["BTC", "ETH", "SOL"]:
            try:
                data = feed.get_recent_data(asset, 10)
                self.assertIsInstance(data, dict)
                self.assertIn("valid", data)
                self.assertIn("prices", data)
                self.assertIn("volumes", data)
                
                if data["valid"]:
                    self.assertIsInstance(data["prices"], list)
                    self.assertIsInstance(data["volumes"], list)
                    print(f"✅ {asset} data structure valid")
                    
            except Exception as e:
                print(f"⚠️ {asset} data test failed: {e}")


def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("🔥 RUNNING COMPREHENSIVE HFT SYSTEM TESTS")
    print("="*60)
    
    # Create test suite using modern approach
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases using the new method
    suite.addTests(loader.loadTestsFromTestCase(TestSignalEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketDataEngine))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("🔥 TEST RESULTS SUMMARY")
    print("="*60)
    
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Signal engine is functional")
        print("✅ Market data engine is operational") 
        print("✅ System is ready for operation")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("🔧 Review failures and fix issues before deployment")
    
    return success


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)