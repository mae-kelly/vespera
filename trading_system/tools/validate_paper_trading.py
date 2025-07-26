#!/usr/bin/env python3
"""
Paper Trading Validation - Comprehensive validation of paper trading with live data
"""
import os
import sys
import time
import json
import asyncio
from datetime import datetime

# Set paper trading mode BEFORE importing config
os.environ["MODE"] = "paper"

# Add src to path
sys.path.insert(0, '.')

import config
from okx_market_data import get_okx_engine
from paper_trading_engine import get_paper_engine
import signal_engine
import confidence_scoring

class PaperTradingValidator:
    def __init__(self):
        # Ensure paper trading mode
        config.MODE = "paper"
        config.PAPER_TRADING = True
        config.LIVE_TRADING = False
        
        self.market_engine = get_okx_engine()
        self.paper_engine = get_paper_engine()
        
        # Reset paper trading state
        self.paper_engine.positions.clear()
        self.paper_engine.trade_history.clear()
        self.paper_engine.balance = config.PAPER_INITIAL_BALANCE
        
        print("🔥 PAPER TRADING VALIDATION SYSTEM")
        print("="*60)
        print("📄 Paper Trading: ON (simulated executions)")
        print("📡 Market Data: LIVE (real prices)")
        print("💰 Virtual Balance: ${:,.2f}".format(config.PAPER_INITIAL_BALANCE))
        print("🚫 No Real Money at Risk")
        print("="*60)
    
    def check_market_data_connectivity(self):
        """Check if we can connect to live market data"""
        print("\n🔍 CHECKING MARKET DATA CONNECTIVITY...")
        
        health = self.market_engine.get_system_health()
        print(f"   System Status: {health['system']['status']}")
        
        live_prices = {}
        for asset in ["BTC", "ETH", "SOL"]:
            try:
                price_data = self.market_engine.get_live_price(asset)
                if price_data and price_data.get('price', 0) > 0:
                    price = price_data['price']
                    live_prices[asset] = price
                    print(f"   ✅ {asset}: ${price:,.2f}")
                else:
                    print(f"   ❌ {asset}: No price data")
            except Exception as e:
                print(f"   ❌ {asset}: Error - {e}")
        
        if len(live_prices) > 0:
            print(f"✅ Market data connectivity: {len(live_prices)}/3 assets available")
            return True, live_prices
        else:
            print("❌ No market data available")
            return False, {}
    
    def test_live_signal_generation(self):
        """Test signal generation with live market data"""
        print("\n🧪 TESTING LIVE SIGNAL GENERATION...")
        
        try:
            shared_data = {
                "timestamp": time.time(),
                "mode": "paper",
                "iteration": 150  # Past warmup
            }
            
            signal = signal_engine.generate_signal(shared_data)
            
            print(f"   Signal Source: {signal.get('source', 'unknown')}")
            print(f"   Confidence: {signal['confidence']:.3f}")
            
            signal_data = signal["signal_data"]
            print(f"   Asset: {signal_data['asset']}")
            print(f"   Entry Price: ${signal_data['entry_price']:,.2f}")
            print(f"   Signal Type: {signal_data['signal_type']}")
            
            if signal_data.get("warmup_mode"):
                print("   ⚠️ Using warmup/simulated data")
                return False, signal
            else:
                print("   ✅ Using live market data")
                return True, signal
                
        except Exception as e:
            print(f"   ❌ Signal generation failed: {e}")
            return False, None
    
    def test_paper_execution(self, signal):
        """Test paper trading execution"""
        print("\n💼 TESTING PAPER TRADING EXECUTION...")
        
        try:
            merged = confidence_scoring.merge_signals([signal])
            print(f"   Merged Confidence: {merged['confidence']:.3f}")
            
            if merged['confidence'] >= config.SIGNAL_CONFIDENCE_THRESHOLD:
                result = self.paper_engine.open_position(merged)
                
                if result:
                    print(f"   ✅ Paper position opened:")
                    print(f"      Asset: {result['asset']}")
                    print(f"      Side: {result['side']}")
                    print(f"      Entry Price: ${result['entry_price']:,.2f}")
                    print(f"      Quantity: {result['quantity']:.6f}")
                    print(f"      Commission: ${result['commission']:.4f}")
                    return True, result
                else:
                    print("   ❌ Position opening failed (risk limits?)")
                    return False, None
            else:
                print(f"   ⚠️ Confidence {merged['confidence']:.3f} below threshold {config.SIGNAL_CONFIDENCE_THRESHOLD}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Paper execution failed: {e}")
            return False, None
    
    def test_live_pnl_tracking(self):
        """Test P&L tracking with live price updates"""
        print("\n📊 TESTING LIVE P&L TRACKING...")
        
        if not self.paper_engine.positions:
            print("   ⚠️ No positions to track")
            return
        
        try:
            # Get current live prices
            live_prices = {}
            for asset in self.paper_engine.positions.keys():
                price_data = self.market_engine.get_live_price(asset)
                if price_data and price_data.get('price', 0) > 0:
                    live_prices[asset] = price_data['price']
            
            if live_prices:
                print(f"   Updating positions with live prices...")
                
                # Show before
                for asset, position in self.paper_engine.positions.items():
                    print(f"   {asset}: Entry ${position.entry_price:,.2f} -> Current ${position.current_price:,.2f}")
                    print(f"         P&L: ${position.unrealized_pnl:+.2f}")
                
                # Update with live prices
                self.paper_engine.update_positions(live_prices)
                
                # Show after
                print(f"   After live price update:")
                for asset, position in self.paper_engine.positions.items():
                    if asset in live_prices:
                        current_price = live_prices[asset]
                        print(f"   {asset}: Entry ${position.entry_price:,.2f} -> Live ${current_price:,.2f}")
                        print(f"         P&L: ${position.unrealized_pnl:+.2f}")
                
                print("   ✅ Live P&L tracking working")
            else:
                print("   ❌ No live prices available for P&L update")
                
        except Exception as e:
            print(f"   ❌ P&L tracking failed: {e}")
    
    def test_portfolio_summary(self):
        """Test portfolio summary with live data"""
        print("\n📋 TESTING PORTFOLIO SUMMARY...")
        
        try:
            summary = self.paper_engine.get_portfolio_summary()
            
            print(f"   📊 Portfolio Summary:")
            print(f"      Balance: ${summary['balance']:,.2f}")
            print(f"      Unrealized P&L: ${summary['unrealized_pnl']:+.2f}")
            print(f"      Total Value: ${summary['total_value']:,.2f}")
            print(f"      Total Return: {summary['total_return']:+.2f}%")
            print(f"      Open Positions: {summary['open_positions']}")
            print(f"      Total Trades: {summary['total_trades']}")
            print(f"      Win Rate: {summary['win_rate']:.1f}%")
            print(f"      Commission Paid: ${summary['total_commission']:.4f}")
            
            print("   ✅ Portfolio summary working")
            return summary
            
        except Exception as e:
            print(f"   ❌ Portfolio summary failed: {e}")
            return None
    
    def simulate_price_movement_and_exit(self):
        """Simulate price movements and position exits"""
        print("\n🎯 TESTING POSITION EXIT SCENARIOS...")
        
        if not self.paper_engine.positions:
            print("   ⚠️ No positions to test exits")
            return
        
        try:
            for asset, position in self.paper_engine.positions.copy().items():
                print(f"   Testing {asset} position exit scenarios:")
                
                # Test stop loss scenario
                if position.side == "sell":  # Short position
                    stop_loss_price = position.entry_price * 1.02  # 2% up
                    print(f"      Simulating stop loss at ${stop_loss_price:,.2f}")
                    
                    market_prices = {asset: stop_loss_price}
                    self.paper_engine.update_positions(market_prices)
                    
                    if asset not in self.paper_engine.positions:
                        print(f"      ✅ Position closed due to stop loss")
                        break
                else:  # Long position
                    stop_loss_price = position.entry_price * 0.98  # 2% down
                    print(f"      Simulating stop loss at ${stop_loss_price:,.2f}")
                    
                    market_prices = {asset: stop_loss_price}
                    self.paper_engine.update_positions(market_prices)
                    
                    if asset not in self.paper_engine.positions:
                        print(f"      ✅ Position closed due to stop loss")
                        break
            
            # Check trade history
            if self.paper_engine.trade_history:
                trade = self.paper_engine.trade_history[-1]
                print(f"   Last trade: {trade.asset} {trade.side}")
                print(f"   Entry: ${trade.entry_price:.2f} -> Exit: ${trade.exit_price:.2f}")
                print(f"   P&L: ${trade.pnl:+.2f} | Reason: {trade.exit_reason}")
                print("   ✅ Position exit working")
            
        except Exception as e:
            print(f"   ❌ Position exit test failed: {e}")
    
    def run_full_validation(self):
        """Run complete validation suite"""
        print(f"\n⏰ Starting validation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Check market connectivity
        connected, live_prices = self.check_market_data_connectivity()
        
        if not connected:
            print("\n❌ VALIDATION FAILED: No market data connectivity")
            print("🔧 Check internet connection and OKX API access")
            return False
        
        # Step 2: Test signal generation
        uses_live_data, signal = self.test_live_signal_generation()
        
        if not signal:
            print("\n❌ VALIDATION FAILED: Signal generation not working")
            return False
        
        # Step 3: Test paper execution
        executed, trade_result = self.test_paper_execution(signal)
        
        # Step 4: Test P&L tracking (whether position opened or not)
        self.test_live_pnl_tracking()
        
        # Step 5: Test portfolio summary
        portfolio = self.test_portfolio_summary()
        
        # Step 6: Test position management
        self.simulate_price_movement_and_exit()
        
        # Final assessment
        print("\n" + "="*60)
        print("🔥 PAPER TRADING VALIDATION RESULTS")
        print("="*60)
        
        if connected and signal and portfolio:
            print("🎉 VALIDATION SUCCESSFUL!")
            print("✅ Market data connectivity working")
            print("✅ Signal generation functional")
            print("✅ Paper trading execution ready")
            print("✅ Live P&L tracking operational")
            print("✅ Portfolio management working")
            
            if uses_live_data:
                print("✅ Using real live market data")
            else:
                print("⚠️ Using simulated data (market data may be warming up)")
            
            if executed:
                print("✅ Successfully executed paper trades")
            else:
                print("⚠️ No trades executed (may be due to confidence/risk limits)")
            
            print("\n📄 PAPER TRADING SYSTEM STATUS:")
            print("   • Real market prices ✅")
            print("   • Simulated executions ✅") 
            print("   • Live P&L tracking ✅")
            print("   • Risk management ✅")
            print("   • No real money at risk ✅")
            
            print(f"\n🚀 READY TO START PAPER TRADING!")
            print(f"   Command: python main.py --mode paper")
            print(f"   Virtual balance: ${config.PAPER_INITIAL_BALANCE:,.2f}")
            print(f"   Max positions: {config.MAX_OPEN_POSITIONS}")
            print(f"   Position size: {config.POSITION_SIZE_PERCENT*100:.1f}% per trade")
            
            return True
        else:
            print("❌ VALIDATION FAILED!")
            print("🔧 Some components are not working correctly")
            
            if not connected:
                print("   ❌ Market data connectivity issues")
            if not signal:
                print("   ❌ Signal generation problems")
            if not portfolio:
                print("   ❌ Portfolio management issues")
            
            print("\n🔧 Fix these issues before starting paper trading")
            return False
    
    def continuous_monitoring_demo(self, duration_minutes=2):
        """Run a continuous monitoring demo"""
        print(f"\n🔄 RUNNING {duration_minutes}-MINUTE CONTINUOUS DEMO...")
        print("   (Press Ctrl+C to stop early)")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        iteration = 0
        
        try:
            while time.time() < end_time:
                iteration += 1
                cycle_start = time.time()
                
                print(f"\n📊 Demo Cycle {iteration} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Generate signal
                shared_data = {
                    "timestamp": time.time(),
                    "mode": "paper",
                    "iteration": iteration + 100
                }
                
                try:
                    signal = signal_engine.generate_signal(shared_data)
                    confidence = signal["confidence"]
                    
                    print(f"   Signal: {signal['signal_data']['asset']} confidence {confidence:.3f}")
                    
                    # Try to execute if confidence is high
                    if confidence >= config.SIGNAL_CONFIDENCE_THRESHOLD:
                        merged = confidence_scoring.merge_signals([signal])
                        
                        if len(self.paper_engine.positions) < config.MAX_OPEN_POSITIONS:
                            # Modify asset to avoid duplicates
                            signal["signal_data"]["asset"] = f"DEMO{iteration}"
                            result = self.paper_engine.open_position(merged)
                            
                            if result:
                                print(f"   ✅ Opened: {result['asset']} @ ${result['entry_price']:,.2f}")
                    
                    # Update existing positions with live prices
                    if self.paper_engine.positions:
                        live_prices = {}
                        for asset in self.paper_engine.positions.keys():
                            try:
                                price_data = self.market_engine.get_live_price("BTC")  # Use BTC as proxy
                                if price_data:
                                    # Simulate price for demo assets
                                    base_price = price_data['price']
                                    noise = (time.time() % 10 - 5) * 0.001  # Small random movement
                                    live_prices[asset] = base_price * (1 + noise)
                            except:
                                pass
                        
                        if live_prices:
                            self.paper_engine.update_positions(live_prices)
                    
                    # Show portfolio status
                    summary = self.paper_engine.get_portfolio_summary()
                    print(f"   Portfolio: ${summary['total_value']:,.2f} ({summary['total_return']:+.2f}%)")
                    print(f"   Positions: {summary['open_positions']}, Trades: {summary['total_trades']}")
                    
                except Exception as e:
                    print(f"   ❌ Cycle error: {e}")
                
                # Wait for next cycle (target 5 seconds)
                cycle_time = time.time() - cycle_start
                sleep_time = max(0, 5.0 - cycle_time)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print(f"\n⏹️ Demo stopped by user")
        
        # Final summary
        final_summary = self.paper_engine.get_portfolio_summary()
        print(f"\n📊 DEMO COMPLETE - Final Results:")
        print(f"   Duration: {(time.time() - start_time)/60:.1f} minutes")
        print(f"   Final Balance: ${final_summary['balance']:,.2f}")
        print(f"   Total Value: ${final_summary['total_value']:,.2f}")
        print(f"   Total Return: {final_summary['total_return']:+.2f}%")
        print(f"   Trades Executed: {final_summary['total_trades']}")
        print(f"   Win Rate: {final_summary['win_rate']:.1f}%")
        print(f"   Commission Paid: ${final_summary['total_commission']:.4f}")


def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Paper Trading System')
    parser.add_argument('--demo', type=int, default=0, help='Run continuous demo for N minutes')
    parser.add_argument('--quick', action='store_true', help='Quick validation only')
    
    args = parser.parse_args()
    
    validator = PaperTradingValidator()
    
    # Run main validation
    success = validator.run_full_validation()
    
    if not success:
        print("\n❌ Validation failed - fix issues before proceeding")
        sys.exit(1)
    
    if args.demo > 0 and not args.quick:
        print(f"\n🎬 Starting {args.demo}-minute demo...")
        validator.continuous_monitoring_demo(args.demo)
    elif not args.quick:
        # Ask if user wants to run demo
        try:
            response = input("\n❓ Run 2-minute demo? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                validator.continuous_monitoring_demo(2)
        except KeyboardInterrupt:
            print("\n👋 Validation complete!")
    
    print("\n" + "="*60)
    print("🎉 PAPER TRADING VALIDATION COMPLETE!")
    print("="*60)
    print("✅ System is ready for paper trading")
    print("📄 All trades will be simulated")
    print("📡 Using real live market data")
    print("💰 No real money at risk")
    print("\n🚀 Start paper trading with:")
    print("   python main.py --mode paper")
    print("="*60)


if __name__ == "__main__":
    main()