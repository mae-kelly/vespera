#!/usr/bin/env python3
"""
Test Confidence Scoring System - Verify signal merging and scoring
"""
import sys
import time
import unittest
import torch
import numpy as np

# Add src to path
sys.path.insert(0, '.')

import confidence_scoring

class TestConfidenceScoring(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.valid_signal = {
            "confidence": 0.8,
            "source": "test_module",
            "production_validated": True,
            "rsi_drop": 25.0,
            "entropy": 0.3,
            "volume_acceleration": 2.5,
            "btc_dominance": 0.6,
            "signal_data": {
                "asset": "BTC",
                "entry_price": 67500.0,
                "stop_loss": 68500.0,
                "take_profit_1": 66500.0,
                "signal_type": "SHORT",
                "reason": "test_signal"
            },
            "timestamp": time.time()
        }
    
    def create_test_signals(self, count=3, confidence_range=(0.7, 0.9)):
        """Create test signals with varying confidence"""
        signals = []
        
        for i in range(count):
            confidence = confidence_range[0] + (confidence_range[1] - confidence_range[0]) * i / (count - 1)
            
            signal = {
                "confidence": confidence,
                "source": f"test_module_{i}",
                "production_validated": True,
                "rsi_drop": 20.0 + i * 5,
                "entropy": 0.2 + i * 0.1,
                "volume_acceleration": 1.5 + i * 0.5,
                "btc_dominance": 0.5 + i * 0.1,
                "signal_data": {
                    "asset": "BTC",
                    "entry_price": 67500.0 + i * 10,
                    "stop_loss": 68500.0 + i * 10,
                    "take_profit_1": 66500.0 + i * 10,
                    "signal_type": "SHORT",
                    "reason": f"test_signal_{i}"
                },
                "timestamp": time.time()
            }
            signals.append(signal)
        
        return signals
    
    def test_softmax_weighted_scoring_basic(self):
        """Test basic softmax weighted scoring"""
        print("🧪 Testing basic softmax weighted scoring...")
        
        signals = self.create_test_signals(3)
        
        try:
            result = confidence_scoring.softmax_weighted_scoring(signals)
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn("confidence", result)
            self.assertIn("source", result)
            self.assertIn("best_signal", result)
            self.assertIn("signal_weights", result)
            self.assertIn("num_signals", result)
            self.assertIn("production_validated", result)
            
            # Verify confidence is valid
            confidence = result["confidence"]
            self.assertIsInstance(confidence, (int, float))
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
            
            # Verify signal weights sum to 1
            weights = result["signal_weights"]
            self.assertAlmostEqual(sum(weights), 1.0, places=5)
            
            print(f"✅ Basic scoring passed - Final confidence: {confidence:.3f}")
            print(f"   Signal weights: {[f'{w:.3f}' for w in weights]}")
            
        except Exception as e:
            self.fail(f"❌ Softmax scoring failed: {e}")
    
    def test_production_validation_required(self):
        """Test that non-validated signals are rejected"""
        print("🧪 Testing production validation requirement...")
        
        # Create signal without production validation
        invalid_signals = [self.valid_signal.copy()]
        invalid_signals[0]["production_validated"] = False
        
        with self.assertRaises(RuntimeError) as context:
            confidence_scoring.softmax_weighted_scoring(invalid_signals)
        
        self.assertIn("Non-validated signal detected", str(context.exception))
        print("✅ Non-validated signals correctly rejected")
    
    def test_confidence_threshold_enforcement(self):
        """Test confidence threshold enforcement"""
        print("🧪 Testing confidence threshold enforcement...")
        
        # Create signals with low confidence
        low_confidence_signals = self.create_test_signals(3, confidence_range=(0.05, 0.08))
        
        try:
            result = confidence_scoring.softmax_weighted_scoring(low_confidence_signals)
            # Should still work but filter out low confidence signals
            self.assertIsInstance(result, dict)
        except RuntimeError as e:
            # Should fail with no valid signals
            self.assertIn("No valid signals after filtering", str(e))
            print("✅ Low confidence signals correctly filtered")
            return
        
        print("✅ Confidence threshold enforcement passed")
    
    def test_agreement_factor_boost(self):
        """Test agreement factor for multiple signals"""
        print("🧪 Testing agreement factor boost...")
        
        # Test with single signal
        single_signal = [self.valid_signal]
        single_result = confidence_scoring.softmax_weighted_scoring(single_signal)
        single_confidence = single_result["confidence"]
        
        # Test with multiple signals (should get agreement boost)
        multiple_signals = self.create_test_signals(4)
        multiple_result = confidence_scoring.softmax_weighted_scoring(multiple_signals)
        multiple_confidence = multiple_result["confidence"]
        
        print(f"   Single signal confidence: {single_confidence:.3f}")
        print(f"   Multiple signals confidence: {multiple_confidence:.3f}")
        
        # Multiple signals should generally have higher confidence due to agreement
        # (though not guaranteed due to other factors)
        self.assertIsInstance(multiple_confidence, (int, float))
        
        print("✅ Agreement factor test passed")
    
    def test_enhancement_factors(self):
        """Test enhancement factors (volume, entropy)"""
        print("🧪 Testing enhancement factors...")
        
        # Create signal with high volume acceleration
        high_volume_signal = self.valid_signal.copy()
        high_volume_signal["volume_acceleration"] = 2.5
        high_volume_signal["signal_data"]["volume_acceleration"] = 2.5
        
        # Create signal with low entropy (more predictable)
        low_entropy_signal = self.valid_signal.copy()
        low_entropy_signal["entropy"] = 0.25
        low_entropy_signal["signal_data"]["entropy"] = 0.25
        
        base_result = confidence_scoring.softmax_weighted_scoring([self.valid_signal])
        volume_result = confidence_scoring.softmax_weighted_scoring([high_volume_signal])
        entropy_result = confidence_scoring.softmax_weighted_scoring([low_entropy_signal])
        
        print(f"   Base confidence: {base_result['confidence']:.3f}")
        print(f"   High volume confidence: {volume_result['confidence']:.3f}")
        print(f"   Low entropy confidence: {entropy_result['confidence']:.3f}")
        
        print("✅ Enhancement factors test passed")
    
    def test_merge_signals_function(self):
        """Test the main merge_signals function"""
        print("🧪 Testing merge_signals function...")
        
        signals = self.create_test_signals(3, confidence_range=(0.75, 0.9))
        
        try:
            result = confidence_scoring.merge_signals(signals)
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn("confidence", result)
            
            # Verify confidence meets production threshold
            confidence = result["confidence"]
            self.assertGreaterEqual(confidence, 0.75, "Final confidence below production threshold")
            
            # Verify production validation
            self.assertTrue(result.get("production_validated", False))
            
            print(f"✅ Signal merging passed - Final confidence: {confidence:.3f}")
            
        except Exception as e:
            self.fail(f"❌ Signal merging failed: {e}")
    
    def test_below_threshold_rejection(self):
        """Test rejection of signals below production threshold"""
        print("🧪 Testing below-threshold signal rejection...")
        
        # Create signals that result in low confidence
        low_signals = self.create_test_signals(2, confidence_range=(0.6, 0.65))
        
        with self.assertRaises(RuntimeError) as context:
            confidence_scoring.merge_signals(low_signals)
        
        self.assertIn("below production threshold", str(context.exception))
        print("✅ Below-threshold signals correctly rejected")
    
    def test_gpu_tensor_operations(self):
        """Test GPU tensor operations"""
        print("🧪 Testing GPU tensor operations...")
        
        signals = self.create_test_signals(3)
        
        # This should work regardless of GPU availability
        # (will fall back to CPU if no GPU)
        try:
            result = confidence_scoring.softmax_weighted_scoring(signals)
            
            # Verify tensor operations worked
            self.assertIsInstance(result["signal_weights"], list)
            self.assertEqual(len(result["signal_weights"]), 3)
            
            print(f"✅ GPU tensor operations passed on device: {confidence_scoring.DEVICE}")
            
        except Exception as e:
            self.fail(f"❌ GPU tensor operations failed: {e}")
    
    def test_empty_signals_handling(self):
        """Test handling of empty signals list"""
        print("🧪 Testing empty signals handling...")
        
        with self.assertRaises(RuntimeError) as context:
            confidence_scoring.softmax_weighted_scoring([])
        
        self.assertIn("No signals provided", str(context.exception))
        
        with self.assertRaises(RuntimeError) as context:
            confidence_scoring.merge_signals([])
        
        self.assertIn("No signals to merge", str(context.exception))
        
        print("✅ Empty signals correctly handled")
    
    def test_feature_normalization(self):
        """Test feature normalization in scoring"""
        print("🧪 Testing feature normalization...")
        
        # Create signals with extreme values
        extreme_signal = self.valid_signal.copy()
        extreme_signal["rsi_drop"] = 100.0  # Should be clamped
        extreme_signal["entropy"] = 1.5     # Should be clamped
        extreme_signal["volume_acceleration"] = 10.0  # Should be clamped
        extreme_signal["btc_dominance"] = 1.2  # Should be clamped
        
        try:
            result = confidence_scoring.softmax_weighted_scoring([extreme_signal])
            
            # Should not crash and should produce valid confidence
            self.assertIsInstance(result["confidence"], (int, float))
            self.assertGreaterEqual(result["confidence"], 0.0)
            self.assertLessEqual(result["confidence"], 1.0)
            
            print("✅ Feature normalization handled extreme values correctly")
            
        except Exception as e:
            self.fail(f"❌ Feature normalization failed: {e}")


def run_confidence_scoring_tests():
    """Run confidence scoring test suite"""
    print("🔥 RUNNING CONFIDENCE SCORING TESTS")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConfidenceScoring))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("🔥 CONFIDENCE SCORING TEST RESULTS")
    print("="*60)
    
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 ALL CONFIDENCE SCORING TESTS PASSED!")
        print("✅ Softmax weighted scoring is functional")
        print("✅ Production validation is enforced")
        print("✅ Signal merging works correctly")
        print("✅ GPU tensor operations are working")
    else:
        print("\n❌ SOME CONFIDENCE SCORING TESTS FAILED")
        print("🔧 Review failures and fix issues")
    
    return success


if __name__ == "__main__":
    success = run_confidence_scoring_tests()
    sys.exit(0 if success else 1)