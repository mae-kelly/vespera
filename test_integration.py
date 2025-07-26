#!/usr/bin/env python3
"""
Integration Tests - Test complete system integration
"""
import sys
import time
import unittest
import tempfile
import json
import threading
import subprocess
import os
import signal

# Add src to path
sys.path.insert(0, '.')

import config
import main
import signal_engine
import confidence_scoring
from paper_trading_engine import get_paper_engine
from okx_market_data import get_okx_engine

class TestSystemIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up integration test environment"""
        # Ensure paper trading mode
        config.MODE = "paper"
        config.PAPER_TRADING = True
        config.LIVE_TRADING = False
        
        # Reset engines
        self.paper_engine = get_paper_engine()
        self.paper_engine.positions.clear()
        self.paper_engine.trade_history.clear()
        self.paper_engine.balance = config.PAPER_INITIAL_BALANCE
    
    def test_signal_to_execution_flow(self):
        """Test complete signal generation to execution flow"""
        print("🧪 Testing signal-to-execution integration...")
        
        # 1. Generate signal
        shared_data = {
            "timestamp": time.time(),
            "mode": "paper",
            "iteration": 50
        }
        
        signal = signal_engine.generate_signal(shared_data)
        self.assertIsInstance(signal, dict)
        self.assertIn("confidence", signal)
        
        # 2. Process through confidence scoring
        signals = [signal]
        merged = confidence_scoring.merge_signals(signals)
        self.assertIsInstance(merged, dict)
        self.assertGreaterEqual(merged["confidence"], 0.75)
        
        # 3. Execute in paper trading
        if merged["confidence"] >= config.SIGNAL_CONFIDENCE_THRESHOLD:
            result = self.paper_engine.open_position(merged)
            self.assertIsNotNone(result)
            
            print(f"✅ Complete flow successful:")
            print(f"   Signal confidence: {merged['confidence']:.3f}")
            print(f"   Position opened: {result['asset']} @ ${result['entry_price']:.2f}")
        
    def test_multi_signal_processing(self):
        """Test processing multiple signals simultaneously"""
        print("🧪 Testing multi-signal processing...")
        
        shared_data = {
            "timestamp": time.time(),
            "mode": "paper",
            "iteration": 75
        }
        
        # Generate multiple signals
        signals = []
        for i in range(3):
            signal = signal_engine.generate_signal(shared_data)
            # Modify slightly to simulate different modules
            signal["source"] = f"module_{i}"
            signals.append(signal)
        
        # Merge signals
        merged = confidence_scoring.merge_signals(signals)
        
        self.assertIsInstance(merged, dict)
        self.assertIn("num_signals", merged)
        self.assertEqual(merged["num_signals"], 3)
        
        print(f"✅ Multi-signal processing successful:")
        print(f"   Combined {len(signals)} signals")
        print(f"   Final confidence: {merged['confidence']:.3f}")
    
    def test_market_data_signal_integration(self):
        """Test integration between market data and signal generation"""
        print("🧪 Testing market data integration...")
        
        # Get market data engine
        market_engine = get_okx_engine()
        health = market_engine.get_system_health()
        
        self.assertIsInstance(health, dict)
        self.assertIn("system", health)
        
        # Generate signal using market data
        shared_data = {
            "timestamp": time.time(),
            "mode": "paper",
            "iteration": 100
        }
        
        signal = signal_engine.generate_signal(shared_data)
        
        # Verify signal includes market data context
        self.assertIn("market_health", signal)
        self.assertEqual(signal["market_health"], health)
        
        print(f"✅ Market data integration successful:")
        print(f"   Market status: {health['system']['status']}")
        print(f"   Signal generated with market context")
    
    def test_position_lifecycle(self):
        """Test complete position lifecycle"""
        print("🧪 Testing position lifecycle...")
        
        # 1. Generate and execute signal
        shared_data = {
            "timestamp": time.time(),
            "mode": "paper",
            "iteration": 50
        }
        
        signal = signal_engine.generate_signal(shared_data)
        merged = confidence_scoring.merge_signals([signal])
        
        # 2. Open position
        result = self.paper_engine.open_position(merged)
        self.assertIsNotNone(result)
        
        asset = result["asset"]
        entry_price = result["entry_price"]
        
        # 3. Simulate price movement and updates
        initial_positions = len(self.paper_engine.positions)
        
        # Simulate profitable movement
        profitable_price = entry_price * 0.98  # 2% down for short position
        market_prices = {asset: profitable_price}
        self.paper_engine.update_positions(market_prices)
        
        # Position should still be open but profitable
        self.assertEqual(len(self.paper_engine.positions), initial_positions)
        position = self.paper_engine.positions[asset]
        self.assertGreater(position.unrealized_pnl, 0)
        
        # 4. Simulate stop loss trigger
        stop_loss_price = entry_price * 1.02  # 2% up for short position
        market_prices = {asset: stop_loss_price}
        self.paper_engine.update_positions(market_prices)
        
        # Position should be closed
        self.assertEqual(len(self.paper_engine.positions), initial_positions - 1)
        self.assertEqual(len(self.paper_engine.trade_history), 1)
        
        trade = self.paper_engine.trade_history[0]
        self.assertEqual(trade.exit_reason, "stop_loss")
        
        print(f"✅ Position lifecycle complete:")
        print(f"   Opened: {asset} @ ${entry_price:.2f}")
        print(f"   Closed: {trade.exit_reason} @ ${stop_loss_price:.2f}")
        print(f"   P&L: ${trade.pnl:.2f}")
    
    def test_risk_management_integration(self):
        """Test risk management integration"""
        print("🧪 Testing risk management integration...")
        
        # Fill up position slots to test limits
        assets = ["BTC", "ETH", "SOL"]
        
        for asset in assets:
            shared_data = {
                "timestamp": time.time(),
                "mode": "paper",
                "iteration": 50
            }
            
            signal = signal_engine.generate_signal(shared_data)
            signal["signal_data"]["asset"] = asset
            
            merged = confidence_scoring.merge_signals([signal])
            result = self.paper_engine.open_position(merged)
            
            if result is not None:
                print(f"   Opened position: {asset}")
        
        # Try to open one more position (should fail)
        extra_signal = signal_engine.generate_signal(shared_data)
        extra_signal["signal_data"]["asset"] = "ADA"
        extra_merged = confidence_scoring.merge_signals([extra_signal])
        extra_result = self.paper_engine.open_position(extra_merged)
        
        self.assertIsNone(extra_result, "Risk management should prevent additional positions")
        
        print("✅ Risk management integration working")
    
    def test_configuration_consistency(self):
        """Test configuration consistency across modules"""
        print("🧪 Testing configuration consistency...")
        
        # Test that all modules use consistent configuration
        self.assertEqual(config.PAPER_TRADING, True)
        self.assertEqual(config.LIVE_TRADING, False)
        self.assertEqual(config.MODE, "paper")
        
        # Test thresholds are consistent
        self.assertIsInstance(config.SIGNAL_CONFIDENCE_THRESHOLD, (int, float))
        self.assertIsInstance(config.POSITION_SIZE_PERCENT, (int, float))
        self.assertIsInstance(config.MAX_OPEN_POSITIONS, int)
        
        # Verify values are reasonable
        self.assertGreater(config.SIGNAL_CONFIDENCE_THRESHOLD, 0.5)
        self.assertLess(config.POSITION_SIZE_PERCENT, 0.1)  # Max 10% per position
        self.assertGreater(config.MAX_OPEN_POSITIONS, 0)
        
        print("✅ Configuration consistency verified")
    
    def test_error_propagation(self):
        """Test error handling and propagation"""
        print("🧪 Testing error propagation...")
        
        # Test signal generation with invalid data
        with self.assertRaises(RuntimeError):
            signal_engine.generate_signal({})
        
        # Test confidence scoring with invalid signals
        invalid_signals = [{"confidence": 0.8, "production_validated": False}]
        with self.assertRaises(RuntimeError):
            confidence_scoring.merge_signals(invalid_signals)
        
        # Test paper trading with invalid signal
        invalid_signal = {"signal_data": {}}
        result = self.paper_engine.open_position(invalid_signal)
        self.assertIsNone(result)
        
        print("✅ Error propagation working correctly")
    
    def test_performance_benchmarks(self):
        """Test system performance benchmarks"""
        print("🧪 Testing performance benchmarks...")
        
        # Test signal generation speed
        start_time = time.time()
        iterations = 10
        
        for i in range(iterations):
            shared_data = {
                "timestamp": time.time(),
                "mode": "paper",
                "iteration": i
            }
            signal = signal_engine.generate_signal(shared_data)
            merged = confidence_scoring.merge_signals([signal])
        
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations
        
        print(f"✅ Performance benchmarks:")
        print(f"   Average signal processing time: {avg_time*1000:.1f}ms")
        print(f"   Target: <100ms per signal")
        
        # Should complete within reasonable time
        self.assertLess(avg_time, 0.1, "Signal processing too slow")
    
    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively"""
        print("🧪 Testing memory usage stability...")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run multiple signal cycles
        for i in range(20):
            shared_data = {
                "timestamp": time.time(),
                "mode": "paper",
                "iteration": i + 100
            }
            
            signal = signal_engine.generate_signal(shared_data)
            merged = confidence_scoring.merge_signals([signal])
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"✅ Memory usage test:")
        print(f"   Initial: {initial_memory:.1f} MB")
        print(f"   Final: {final_memory:.1f} MB")
        print(f"   Increase: {memory_increase:.1f} MB")
        
        # Should not increase significantly
        self.assertLess(memory_increase, 50, "Memory usage increased too much")


def run_integration_tests():
    """Run integration test suite"""
    print("🔥 RUNNING INTEGRATION TESTS")
    print("="*60)
    print("🔗 Testing complete system integration")
    print("📊 End-to-end workflow validation")
    print("="*60)
    
    # Ensure paper trading mode
    config.MODE = "paper"
    config.PAPER_TRADING = True
    config.LIVE_TRADING = False
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("🔥 INTEGRATION TEST RESULTS")
    print("="*60)
    
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ INTEGRATION FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n💥 INTEGRATION ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Signal-to-execution flow working")
        print("✅ Multi-signal processing functional")
        print("✅ Market data integration operational")
        print("✅ Position lifecycle management working")
        print("✅ Risk management enforced")
        print("✅ System configuration consistent")
        print("✅ Error handling proper")
        print("✅ Memory usage stable")
    else:
        print("\n❌ SOME INTEGRATION TESTS FAILED")
        print("🔧 Review integration issues and fix")
    
    return success


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)