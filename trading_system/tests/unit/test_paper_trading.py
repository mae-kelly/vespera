#!/usr/bin/env python3
"""
Test Paper Trading Engine - Verify paper trading functionality
"""
import sys
import time
import unittest
import tempfile
import json

# Add src to path
sys.path.insert(0, '.')

import config
from paper_trading_engine import get_paper_engine, PaperPosition, PaperTrade

class TestPaperTradingEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        # Reset paper trading engine
        global paper_engine
        paper_engine = get_paper_engine()
        
        # Clear any existing positions
        paper_engine.positions.clear()
        paper_engine.trade_history.clear()
        paper_engine.balance = config.PAPER_INITIAL_BALANCE
        paper_engine.total_trades = 0
        paper_engine.winning_trades = 0
        paper_engine.total_commission = 0.0
        
        # Sample signal data
        self.sample_signal = {
            "confidence": 0.85,
            "signal_data": {
                "asset": "BTC",
                "entry_price": 67500.0,
                "stop_loss": 68500.0,
                "take_profit_1": 66500.0,
                "signal_type": "SHORT"
            }
        }
    
    def test_paper_engine_initialization(self):
        """Test paper trading engine initialization"""
        print("🧪 Testing paper engine initialization...")
        
        engine = get_paper_engine()
        
        self.assertIsNotNone(engine)
        self.assertEqual(engine.balance, config.PAPER_INITIAL_BALANCE)
        self.assertEqual(engine.initial_balance, config.PAPER_INITIAL_BALANCE)
        self.assertEqual(len(engine.positions), 0)
        self.assertEqual(len(engine.trade_history), 0)
        
        print(f"✅ Paper engine initialized with ${engine.balance:,.2f}")
    
    def test_position_opening(self):
        """Test opening a paper position"""
        print("🧪 Testing position opening...")
        
        engine = get_paper_engine()
        initial_balance = engine.balance
        
        result = engine.open_position(self.sample_signal)
        
        self.assertIsNotNone(result)
        self.assertIn("position_id", result)
        self.assertIn("asset", result)
        self.assertIn("side", result)
        self.assertIn("entry_price", result)
        self.assertIn("quantity", result)
        self.assertIn("commission", result)
        
        # Check position was created
        self.assertEqual(len(engine.positions), 1)
        self.assertIn("BTC", engine.positions)
        
        # Check balance decreased by commission
        self.assertLess(engine.balance, initial_balance)
        
        position = engine.positions["BTC"]
        self.assertEqual(position.asset, "BTC")
        self.assertEqual(position.entry_price, 67500.0)
        self.assertGreater(position.quantity, 0)
        
        print(f"✅ Position opened: {position.asset} {position.side} @ ${position.entry_price:.2f}")
        print(f"   Quantity: {position.quantity:.6f}")
        print(f"   Commission: ${result['commission']:.2f}")
    
    def test_position_size_calculation(self):
        """Test position size calculation"""
        print("🧪 Testing position size calculation...")
        
        engine = get_paper_engine()
        
        entry_price = 67500.0
        position_size = engine.get_position_size(entry_price)
        position_value = position_size * entry_price
        
        expected_max_value = engine.balance * config.POSITION_SIZE_PERCENT
        
        self.assertGreater(position_size, 0)
        self.assertLessEqual(position_value, expected_max_value * 1.01)  # Small tolerance
        
        print(f"✅ Position size: {position_size:.6f} (value: ${position_value:.2f})")
        print(f"   Max allowed: ${expected_max_value:.2f}")
    
    def test_position_limits(self):
        """Test position opening limits"""
        print("🧪 Testing position limits...")
        
        engine = get_paper_engine()
        
        # Open multiple positions up to limit
        assets = ["BTC", "ETH", "SOL"]
        
        for i, asset in enumerate(assets):
            signal = self.sample_signal.copy()
            signal["signal_data"]["asset"] = asset
            signal["signal_data"]["entry_price"] = 1000.0 * (i + 1)
            
            result = engine.open_position(signal)
            self.assertIsNotNone(result, f"Failed to open position for {asset}")
        
        # Try to open one more (should fail due to max positions limit)
        extra_signal = self.sample_signal.copy()
        extra_signal["signal_data"]["asset"] = "ADA"
        result = engine.open_position(extra_signal)
        self.assertIsNone(result, "Should not allow opening position beyond limit")
        
        print(f"✅ Position limits enforced: {len(engine.positions)}/{config.MAX_OPEN_POSITIONS}")
    
    def test_duplicate_position_prevention(self):
        """Test prevention of duplicate positions"""
        print("🧪 Testing duplicate position prevention...")
        
        engine = get_paper_engine()
        
        # Open first position
        result1 = engine.open_position(self.sample_signal)
        self.assertIsNotNone(result1)
        
        # Try to open duplicate position for same asset
        result2 = engine.open_position(self.sample_signal)
        self.assertIsNone(result2, "Should not allow duplicate position for same asset")
        
        print("✅ Duplicate position prevention works")
    
    def test_pnl_calculation(self):
        """Test P&L calculation"""
        print("🧪 Testing P&L calculation...")
        
        engine = get_paper_engine()
        
        # Open position
        result = engine.open_position(self.sample_signal)
        self.assertIsNotNone(result)
        
        position = engine.positions["BTC"]
        
        # Test profit scenario (price goes down for short position)
        profitable_price = 66000.0  # Lower than entry price
        position.update_pnl(profitable_price)
        self.assertGreater(position.unrealized_pnl, 0, "Should be profitable")
        
        # Test loss scenario (price goes up for short position)
        loss_price = 69000.0  # Higher than entry price
        position.update_pnl(loss_price)
        self.assertLess(position.unrealized_pnl, 0, "Should be at loss")
        
        print(f"✅ P&L calculation works correctly")
        print(f"   Profit at ${profitable_price}: ${(67500 - profitable_price) * position.quantity:.2f}")
        print(f"   Loss at ${loss_price}: ${(67500 - loss_price) * position.quantity:.2f}")
    
    def test_position_updates_and_closing(self):
        """Test position updates and closing"""
        print("🧪 Testing position updates and closing...")
        
        engine = get_paper_engine()
        
        # Open position
        result = engine.open_position(self.sample_signal)
        self.assertIsNotNone(result)
        
        initial_positions = len(engine.positions)
        initial_trades = len(engine.trade_history)
        
        # Update with market prices that should trigger stop loss
        market_prices = {"BTC": 69000.0}  # Above stop loss for short position
        engine.update_positions(market_prices)
        
        # Position should be closed
        self.assertEqual(len(engine.positions), initial_positions - 1)
        self.assertEqual(len(engine.trade_history), initial_trades + 1)
        
        # Check trade was recorded
        trade = engine.trade_history[-1]
        self.assertEqual(trade.asset, "BTC")
        self.assertEqual(trade.exit_reason, "stop_loss")
        
        print("✅ Position closing works correctly")
        print(f"   Closed due to: {trade.exit_reason}")
    
    def test_portfolio_summary(self):
        """Test portfolio summary generation"""
        print("🧪 Testing portfolio summary...")
        
        engine = get_paper_engine()
        
        # Get initial summary
        summary = engine.get_portfolio_summary()
        
        self.assertIsInstance(summary, dict)
        required_fields = [
            "balance", "unrealized_pnl", "total_value", "total_return",
            "open_positions", "total_trades", "winning_trades", "win_rate",
            "total_commission", "max_drawdown", "daily_trades_today"
        ]
        
        for field in required_fields:
            self.assertIn(field, summary, f"Missing field: {field}")
        
        # Verify initial values
        self.assertEqual(summary["balance"], config.PAPER_INITIAL_BALANCE)
        self.assertEqual(summary["total_return"], 0.0)
        self.assertEqual(summary["open_positions"], 0)
        
        print("✅ Portfolio summary structure correct")
        print(f"   Initial balance: ${summary['balance']:,.2f}")
        print(f"   Total value: ${summary['total_value']:,.2f}")
    
    def test_positions_display(self):
        """Test positions display format"""
        print("🧪 Testing positions display...")
        
        engine = get_paper_engine()
        
        # Open a position
        result = engine.open_position(self.sample_signal)
        self.assertIsNotNone(result)
        
        # Get positions display
        positions = engine.get_positions_display()
        
        self.assertEqual(len(positions), 1)
        
        position_display = positions[0]
        required_fields = [
            "asset", "side", "entry_price", "current_price", "quantity",
            "unrealized_pnl", "stop_loss", "take_profit", "duration"
        ]
        
        for field in required_fields:
            self.assertIn(field, position_display, f"Missing field: {field}")
        
        print("✅ Positions display format correct")
        print(f"   {position_display['asset']} {position_display['side']} @ ${position_display['entry_price']:.2f}")
    
    def test_state_saving(self):
        """Test state saving functionality"""
        print("🧪 Testing state saving...")
        
        engine = get_paper_engine()
        
        # Open a position
        result = engine.open_position(self.sample_signal)
        self.assertIsNotNone(result)
        
        # Save state
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
        
        try:
            engine.save_state(temp_filename)
            
            # Verify file was created and contains valid JSON
            with open(temp_filename, 'r') as f:
                state = json.load(f)
            
            self.assertIsInstance(state, dict)
            self.assertIn("balance", state)
            self.assertIn("positions", state)
            self.assertIn("statistics", state)
            
            print("✅ State saving works correctly")
            
        finally:
            import os
            try:
                os.unlink(temp_filename)
            except:
                pass
    
    def test_commission_calculation(self):
        """Test commission calculation"""
        print("🧪 Testing commission calculation...")
        
        engine = get_paper_engine()
        
        initial_commission = engine.total_commission
        
        # Open position
        result = engine.open_position(self.sample_signal)
        self.assertIsNotNone(result)
        
        # Commission should have increased
        self.assertGreater(engine.total_commission, initial_commission)
        
        expected_commission = result["quantity"] * result["entry_price"] * config.PAPER_COMMISSION_RATE
        actual_commission = engine.total_commission - initial_commission
        
        self.assertAlmostEqual(actual_commission, expected_commission, places=6)
        
        print(f"✅ Commission calculation correct: ${actual_commission:.6f}")


def run_paper_trading_tests():
    """Run paper trading test suite"""
    print("🔥 RUNNING PAPER TRADING TESTS")
    print("="*60)
    
    # Ensure paper trading mode
    config.MODE = "paper"
    config.PAPER_TRADING = True
    config.LIVE_TRADING = False
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPaperTradingEngine))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("🔥 PAPER TRADING TEST RESULTS")
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
        print("\n🎉 ALL PAPER TRADING TESTS PASSED!")
        print("✅ Paper trading engine is functional")
        print("✅ Position management works correctly")
        print("✅ P&L calculations are accurate")
        print("✅ Risk limits are enforced")
        print("✅ Portfolio tracking is working")
    else:
        print("\n❌ SOME PAPER TRADING TESTS FAILED")
        print("🔧 Review failures and fix issues")
    
    return success


if __name__ == "__main__":
    success = run_paper_trading_tests()
    sys.exit(0 if success else 1)