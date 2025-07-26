import unittest
import time
import json
import os
import tempfile
import signal_engine
import confidence_scoring
import config

class TestSignalEngine(unittest.TestCase):
    def setUp(self):
        signal_engine.feed.start_feed()
        time.sleep(1)
        
    def test_rsi_calculation(self):
        prices = [100, 101, 99, 102, 98, 103, 97, 104]
        rsi = signal_engine.calculate_rsi_torch(prices)
        self.assertIsInstance(rsi, float)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
        
    def test_vwap_calculation(self):
        prices = [100, 101, 102]
        volumes = [1000, 1100, 900]
        vwap = signal_engine.calculate_vwap(prices, volumes)
        self.assertIsInstance(vwap, float)
        self.assertGreater(vwap, 0)
        
    def test_volume_anomaly_detection(self):
        volumes = [1000, 1100, 1050, 2000]
        anomaly = signal_engine.detect_volume_anomaly(volumes)
        self.assertIsInstance(anomaly, bool)
        
    def test_signal_generation(self):
        shared_data = {"timestamp": time.time(), "mode": "dry", "iteration": 1}
        signal = signal_engine.generate_signal(shared_data)
        self.assertIn("confidence", signal)
        self.assertIn("source", signal)
        self.assertIsInstance(signal["confidence"], float)

class TestConfidenceScoring(unittest.TestCase):
    def test_softmax_weighted_sum(self):
        components = {"rsi_drop": 0.5, "entropy_decay": 0.3}
        weights = {"rsi_drop": 0.6, "entropy_decay": 0.4}
        result = confidence_scoring.softmax_weighted_sum(components, weights)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)
        
    def test_merge_signals(self):
        signals = [
            {"confidence": 0.7, "source": "test", "priority": 1, "entropy": 0.0}
        ]
        merged = confidence_scoring.merge_signals(signals)
        self.assertIn("confidence", merged)
        self.assertIsInstance(merged["confidence"], float)

class TestConfig(unittest.TestCase):
    def test_config_validation(self):
        errors = config.validate_config()
        self.assertIsInstance(errors, list)

if __name__ == "__main__":
    unittest.main()
