#!/usr/bin/env python3
"""
HFT Trading System - Pure Live Data Paper Trading
NO simulated data - everything must come from OKX live feeds
"""

import sys
import time
import json
import logging
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

# Set up logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/trading.log')
    ]
)

# Create logs directory
Path("logs").mkdir(exist_ok=True)

# Global paper engine variable
paper_engine = None

try:
    import config
    import signal_engine
    import confidence_scoring
    
    # Force paper trading mode regardless of config
    if config.MODE == "paper" or not hasattr(config, 'LIVE_TRADING') or not config.LIVE_TRADING:
        from paper_trading_engine import get_paper_engine
        paper_engine = get_paper_engine()
        logging.info("✅ Paper trading engine initialized")
        
except ImportError as e:
    logging.error(f"Critical import failed: {e}")
    print("❌ Import Error: Please run 'python3 quick_start.py' first")
    sys.exit(1)

class LiveDataPaperTradingSystem:
    def __init__(self, mode="paper"):
        self.mode = mode
        self.running = True
        self.iteration = 0
        self.executor = ThreadPoolExecutor(max_workers=2)  # Reduced workers
        self.last_display = time.time()
        self.market_data_ready = False
        self.last_signal_time = 0
        
        # Initialize global paper engine
        global paper_engine
        if paper_engine is None:
            try:
                from paper_trading_engine import get_paper_engine
                paper_engine = get_paper_engine()
                logging.info("✅ Paper trading engine initialized globally")
            except Exception as e:
                logging.error(f"Failed to initialize paper engine: {e}")
                sys.exit(1)
        
        # Signal modules
        self.signal_modules = [('live_data', signal_engine.generate_signal)]
        
        logging.info(f"🚀 LIVE DATA PAPER TRADING SYSTEM STARTED")
        logging.info(f"📄 Virtual balance: ${config.PAPER_INITIAL_BALANCE:,.0f}")
        logging.info("⚠️  NO SIMULATED DATA - 100% live OKX market data only")
    
    def wait_for_live_data(self):
        """Wait for OKX live data to be available - NO FALLBACKS"""
        try:
            from okx_market_data import get_okx_engine
            feed = get_okx_engine()
            
            max_wait_iterations = 60  # 2 minutes max wait
            wait_count = 0
            
            while wait_count < max_wait_iterations:
                health = feed.get_system_health()
                status = health['system']['status']
                
                if status == 'LIVE':
                    # Double-check we have actual price data
                    try:
                        btc_price = feed.get_live_price("BTC")
                        if btc_price and btc_price.get('price', 0) > 0:
                            logging.info("🔥 LIVE MARKET DATA CONFIRMED - Trading ready")
                            return True
                    except:
                        pass
                
                wait_count += 1
                if wait_count % 10 == 0:
                    logging.info(f"⏳ Waiting for live data... Status: {status} ({wait_count}/60)")
                
                time.sleep(2)
            
            raise RuntimeError("TIMEOUT: Live market data not available after 2 minutes")
            
        except Exception as e:
            raise RuntimeError(f"LIVE DATA ERROR: {e}")
    
    def check_market_data_quality(self):
        """Verify live data quality before signal generation"""
        try:
            from okx_market_data import get_okx_engine
            feed = get_okx_engine()
            
            # Check all required assets have live data
            for asset in ["BTC", "ETH", "SOL"]:
                price_data = feed.get_live_price(asset)
                if not price_data or price_data.get('price', 0) <= 0:
                    return False
                
                # Check data freshness
                timestamp = price_data.get('timestamp', 0)
                age = time.time() - timestamp
                if age > 30:  # Data older than 30 seconds
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Market data quality check failed: {e}")
            return False
    
    def run_signal_module(self, module_name, func, shared_data):
        """Run signal generation with live data only"""
        try:
            start_time = time.time()
            result = func(shared_data)
            execution_time = (time.time() - start_time) * 1000
            
            if result and isinstance(result, dict):
                result['execution_time_ms'] = execution_time
                result['module'] = module_name
                
                # Validate this is truly live data
                signal_data = result.get('signal_data', {})
                if not signal_data.get('live_data_timestamp'):
                    raise RuntimeError("SIGNAL REJECTED: Not live data")
                
                return result
            else:
                return None
                
        except Exception as e:
            # Only log errors, don't crash - market conditions change
            logging.warning(f"Signal generation: {e}")
            return None
    
    def generate_live_signals(self, shared_data):
        """Generate signals from live data only"""
        # Verify data quality first
        if not self.check_market_data_quality():
            return []
        
        futures = []
        for module_name, func in self.signal_modules:
            future = self.executor.submit(self.run_signal_module, module_name, func, shared_data)
            futures.append(future)
        
        signals = []
        for future in as_completed(futures, timeout=8.0):
            try:
                signal = future.result()
                if signal and signal.get("confidence", 0) > 0.5:  # Only high-quality signals
                    signals.append(signal)
            except Exception as e:
                logging.debug(f"Signal future failed: {e}")
                continue
        
        return signals
    
    def handle_paper_trading(self, signal_data: Dict):
        """Execute paper trades based on live signals"""
        global paper_engine
        
        if paper_engine is None:
            logging.error("Paper engine not available")
            return
            
        try:
            confidence = signal_data.get("confidence", 0)
            
            if confidence >= config.SIGNAL_CONFIDENCE_THRESHOLD:
                result = paper_engine.open_position(signal_data)
                
                if result:
                    signal_info = signal_data.get('signal_data', {})
                    logging.info(f"📄 LIVE DATA TRADE: {result['asset']} {result['side']} @ ${result['entry_price']:.2f} | RSI:{signal_info.get('rsi', 0):.1f} | Conf:{confidence:.3f}")
                    
                    # Write signal for monitoring
                    with open("/tmp/signal.json", "w") as f:
                        json.dump(signal_data, f, indent=2)
                else:
                    logging.debug("Paper trade not executed (position limits or constraints)")
            else:
                logging.debug(f"Signal below threshold: {confidence:.3f}")
                
        except Exception as e:
            logging.error(f"Paper trading execution error: {e}")
    
    def update_paper_positions(self):
        """Update positions with live market prices"""
        global paper_engine
        
        if paper_engine is None:
            return
        
        try:
            from okx_market_data import get_okx_engine
            feed = get_okx_engine()
            
            # Get live prices for all assets
            market_prices = {}
            for asset in config.ASSETS:
                try:
                    price_data = feed.get_live_price(asset)
                    if price_data and price_data.get('price', 0) > 0:
                        market_prices[asset] = price_data['price']
                except Exception:
                    continue
            
            if market_prices:
                paper_engine.update_positions(market_prices)
                logging.debug(f"Updated positions with live prices: {market_prices}")
            else:
                logging.warning("No live prices available for position updates")
        
        except Exception as e:
            logging.error(f"Error updating paper positions: {e}")
    
    def display_portfolio_status(self):
        """Display portfolio status every 60 seconds"""
        global paper_engine
        
        if paper_engine is None:
            return
        
        # Display every 60 seconds
        if time.time() - self.last_display < 60:
            return
        
        try:
            summary = paper_engine.get_portfolio_summary()
            positions = paper_engine.get_positions_display()
            
            print("\n" + "="*70)
            print("📄 LIVE DATA PAPER TRADING - PORTFOLIO STATUS")
            print("="*70)
            print(f"💰 Balance: ${summary['balance']:,.2f}")
            print(f"📈 Unrealized P&L: ${summary['unrealized_pnl']:+.2f}")
            print(f"💵 Total Value: ${summary['total_value']:,.2f}")
            print(f"📊 Total Return: {summary['total_return']:+.2f}%")
            print(f"🎯 Win Rate: {summary['win_rate']:.1f}% ({summary['winning_trades']}/{summary['total_trades']})")
            print(f"📉 Max Drawdown: {summary['max_drawdown']:.2f}%")
            print(f"📅 Today's Trades: {summary['daily_trades_today']}")
            
            if positions:
                print(f"\n🔥 Open Positions ({len(positions)}) - LIVE DATA:")
                for pos in positions:
                    duration_mins = int(pos['duration'] / 60)
                    pnl_pct = (pos['unrealized_pnl'] / (pos['entry_price'] * pos['quantity'])) * 100
                    print(f"  {pos['asset']} {pos['side'].upper()}: "
                          f"${pos['entry_price']:.2f} → ${pos['current_price']:.2f} "
                          f"(P&L: ${pos['unrealized_pnl']:+.2f} | {pnl_pct:+.2f}%) [{duration_mins}m]")
            else:
                print("\n💤 No open positions")
            
            print("="*70)
            
            self.last_display = time.time()
            paper_engine.save_state()
            
        except Exception as e:
            logging.error(f"Error displaying portfolio: {e}")
    
    def run(self):
        """Main trading loop - 100% live data driven"""
        logging.info("🚀 Starting live data paper trading system...")
        
        # Wait for live market data
        try:
            self.wait_for_live_data()
        except Exception as e:
            logging.error(f"Failed to get live data: {e}")
            sys.exit(1)
        
        logging.info("✅ LIVE DATA CONFIRMED - Starting trading loop")
        
        while self.running:
            try:
                self.iteration += 1
                loop_start = time.time()
                
                shared_data = {
                    "timestamp": time.time(),
                    "mode": self.mode,
                    "iteration": self.iteration
                }
                
                # Generate signals from live data
                signals = self.generate_live_signals(shared_data)
                
                if signals:
                    try:
                        # Merge and process signals
                        merged = confidence_scoring.merge_signals(signals)
                        confidence = merged.get("confidence", 0)
                        
                        # Handle paper trading
                        self.handle_paper_trading(merged)
                        self.last_signal_time = time.time()
                        
                    except Exception as e:
                        logging.error(f"Signal processing error: {e}")
                        continue
                
                # Update positions with live prices
                self.update_paper_positions()
                
                # Display portfolio status
                self.display_portfolio_status()
                
                # Progress indicator
                if self.iteration % 30 == 0:
                    logging.info(f"🔄 System running - Iteration {self.iteration} | Last signal: {int(time.time() - self.last_signal_time)}s ago")
                
                # Maintain 2-second cycle
                cycle_time = time.time() - loop_start
                sleep_time = max(0, 2.0 - cycle_time)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logging.info("Shutting down live data paper trading system...")
                break
            except Exception as e:
                logging.error(f"System error: {e}")
                time.sleep(2)  # Brief pause before continuing
        
        # Cleanup and final summary
        self.executor.shutdown(wait=True)
        
        try:
            global paper_engine
            if paper_engine:
                print("\n" + "="*70)
                print("📄 FINAL LIVE DATA PAPER TRADING RESULTS")
                print("="*70)
                summary = paper_engine.get_portfolio_summary()
                print(f"💰 Final Balance: ${summary['balance']:,.2f}")
                print(f"💵 Total Value: ${summary['total_value']:,.2f}")
                print(f"📊 Total Return: {summary['total_return']:+.2f}%")
                print(f"🎯 Win Rate: {summary['win_rate']:.1f}%")
                print(f"📉 Max Drawdown: {summary['max_drawdown']:.2f}%")
                print(f"💸 Total Commission: ${summary['total_commission']:.2f}")
                print("✅ ALL TRADES BASED ON LIVE OKX DATA")
                print("="*70)
        except Exception as e:
            logging.error(f"Error displaying final summary: {e}")

def main():
    parser = argparse.ArgumentParser(description='Live Data Paper Trading System')
    parser.add_argument('--mode', choices=['paper', 'live'], default='paper',
                       help='Trading mode: paper (default) or live')
    args = parser.parse_args()
    
    if args.mode == "live":
        print("❌ Live trading not implemented in this version")
        print("   This system is for LIVE DATA PAPER TRADING only")
        sys.exit(1)
    
    system = LiveDataPaperTradingSystem(mode="paper")
    try:
        system.run()
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()