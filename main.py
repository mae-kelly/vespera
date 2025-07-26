#!/usr/bin/env python3
import torch
import sys
import time
import json
import logging
import importlib
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

import config
import signal_engine
import confidence_scoring

# Import paper trading if in paper mode
if config.PAPER_TRADING:
    from paper_trading_engine import get_paper_engine
    paper_engine = get_paper_engine()

class HFTSystem:
    def __init__(self, mode="paper"):
        self.mode = mode
        self.running = True
        self.iteration = 0
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.last_reload = time.time()
        self.last_display = time.time()
        
        self.signal_modules = [('main', signal_engine.generate_signal)]
        
        Path("/tmp").mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        mode_str = "PAPER TRADING" if config.PAPER_TRADING else "LIVE TRADING"
        logging.info(f"🚀 HFT System started in {mode_str} mode")
        
        if config.PAPER_TRADING:
            logging.info(f"📄 Starting with ${config.PAPER_INITIAL_BALANCE:,.0f} virtual balance")
    
    def reload_modules_if_needed(self):
        if time.time() - self.last_reload > 60:
            try:
                importlib.reload(signal_engine)
                importlib.reload(confidence_scoring)
                logging.info("Modules reloaded")
                self.last_reload = time.time()
            except Exception as e:
                logging.error(f"Module reload failed: {e}")
    
    def run_signal_module(self, module_name, func, shared_data):
        try:
            start_time = time.time()
            result = func(shared_data)
            execution_time = (time.time() - start_time) * 1000
            result['execution_time_ms'] = execution_time
            result['module'] = module_name
            return result
        except Exception as e:
            raise RuntimeError(f"Signal module {module_name} failed: {e}")
    
    def generate_concurrent_signals(self, shared_data):
        futures = []
        
        for module_name, func in self.signal_modules:
            future = self.executor.submit(self.run_signal_module, module_name, func, shared_data)
            futures.append(future)
        
        signals = []
        for future in as_completed(futures, timeout=10.0):
            try:
                signal = future.result()
                confidence = signal.get("confidence")
                if confidence is None:
                    logging.warning("Signal missing confidence")
                    continue
                if confidence > 0.1:
                    signals.append(signal)
            except Exception as e:
                logging.error(f"Future completion failed: {e}")
                continue
        
        return signals
    
    def handle_paper_trading(self, signal_data: Dict):
        """Handle paper trading execution"""
        confidence = signal_data.get("confidence", 0)
        
        if confidence >= config.SIGNAL_CONFIDENCE_THRESHOLD:
            # Attempt to open paper position
            result = paper_engine.open_position(signal_data)
            
            if result:
                logging.info(f"📄 Paper trade executed: {result['asset']} {result['side']}")
                # Write to signal file for consistency
                with open("/tmp/signal.json", "w") as f:
                    json.dump(signal_data, f, indent=2)
        else:
            logging.debug(f"Signal below threshold: {confidence:.3f}")
    
    def update_paper_positions(self):
        """Update paper trading positions with current market data"""
        if not config.PAPER_TRADING:
            return
        
        try:
            from okx_market_data import get_okx_engine
            feed = get_okx_engine()
            
            # Get current prices for all assets
            market_prices = {}
            for asset in config.ASSETS:
                try:
                    price_data = feed.get_live_price(asset)
                    if price_data and price_data.get('price', 0) > 0:
                        market_prices[asset] = price_data['price']
                except Exception as e:
                    logging.debug(f"Could not get price for {asset}: {e}")
            
            if market_prices:
                paper_engine.update_positions(market_prices)
        
        except Exception as e:
            logging.error(f"Error updating paper positions: {e}")
    
    def display_portfolio_status(self):
        """Display current portfolio status"""
        if not config.PAPER_TRADING:
            return
        
        # Display every 10 seconds
        if time.time() - self.last_display < 10:
            return
        
        try:
            summary = paper_engine.get_portfolio_summary()
            positions = paper_engine.get_positions_display()
            
            print("\n" + "="*60)
            print("📄 PAPER TRADING PORTFOLIO STATUS")
            print("="*60)
            print(f"💰 Balance: ${summary['balance']:,.2f}")
            print(f"📈 Unrealized P&L: ${summary['unrealized_pnl']:+.2f}")
            print(f"💵 Total Value: ${summary['total_value']:,.2f}")
            print(f"📊 Total Return: {summary['total_return']:+.2f}%")
            print(f"🎯 Win Rate: {summary['win_rate']:.1f}% ({summary['winning_trades']}/{summary['total_trades']})")
            print(f"📉 Max Drawdown: {summary['max_drawdown']:.2f}%")
            print(f"📅 Today's Trades: {summary['daily_trades_today']}")
            
            if positions:
                print(f"\n🔥 Open Positions ({len(positions)}):")
                for pos in positions:
                    duration_mins = int(pos['duration'] / 60)
                    print(f"  {pos['asset']} {pos['side'].upper()}: "
                          f"${pos['entry_price']:.2f} → ${pos['current_price']:.2f} "
                          f"(P&L: ${pos['unrealized_pnl']:+.2f}) [{duration_mins}m]")
            else:
                print("\n💤 No open positions")
            
            print("="*60)
            
            self.last_display = time.time()
            
            # Save state periodically
            paper_engine.save_state()
            
        except Exception as e:
            logging.error(f"Error displaying portfolio: {e}")
    
    def run(self):
        logging.info("Starting main system loop...")
        
        while self.running:
            try:
                self.iteration += 1
                start_time = time.time()
                
                self.reload_modules_if_needed()
                
                shared_data = {
                    "timestamp": time.time(),
                    "mode": self.mode,
                    "iteration": self.iteration
                }
                
                signals = self.generate_concurrent_signals(shared_data)
                
                if signals:
                    merged = confidence_scoring.merge_signals(signals)
                    confidence = merged.get("confidence", 0)
                    
                    if config.PAPER_TRADING:
                        # Handle paper trading
                        self.handle_paper_trading(merged)
                        self.update_paper_positions()
                        self.display_portfolio_status()
                    else:
                        # Handle live trading
                        if confidence >= config.SIGNAL_CONFIDENCE_THRESHOLD:
                            with open("/tmp/signal.json", "w") as f:
                                json.dump(merged, f, indent=2)
                            logging.info(f"Live signal: {confidence:.3f} from {len(signals)} modules")
                        else:
                            logging.debug(f"Signal below threshold: {confidence:.3f}")
                else:
                    if self.iteration % 10 == 0:  # Reduced frequency
                        logging.debug("No signals generated this cycle")
                
                cycle_time = time.time() - start_time
                sleep_time = max(0, 2.0 - cycle_time)  # 2 second cycles for paper trading
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logging.info("Shutting down system...")
                break
            except Exception as e:
                logging.error(f"System error: {e}")
                if config.LIVE_TRADING:
                    # In live trading, crash on errors
                    raise
                else:
                    # In paper trading, continue running
                    time.sleep(1)
        
        self.executor.shutdown(wait=True)
        
        if config.PAPER_TRADING:
            # Final portfolio summary
            print("\n" + "="*60)
            print("📄 FINAL PAPER TRADING RESULTS")
            print("="*60)
            summary = paper_engine.get_portfolio_summary()
            print(f"💰 Final Balance: ${summary['balance']:,.2f}")
            print(f"💵 Total Value: ${summary['total_value']:,.2f}")
            print(f"📊 Total Return: {summary['total_return']:+.2f}%")
            print(f"🎯 Win Rate: {summary['win_rate']:.1f}%")
            print(f"📉 Max Drawdown: {summary['max_drawdown']:.2f}%")
            print(f"💸 Total Commission: ${summary['total_commission']:.2f}")
            print("="*60)

def main():
    parser = argparse.ArgumentParser(description='HFT Trading System')
    parser.add_argument('--mode', choices=['paper', 'live'], default='paper',
                       help='Trading mode: paper (default) or live')
    args = parser.parse_args()
    
    # Override config with command line argument
    config.MODE = args.mode
    config.PAPER_TRADING = args.mode == "paper"
    config.LIVE_TRADING = args.mode == "live"
    
    if config.LIVE_TRADING and not all([
        config.OKX_API_KEY, config.OKX_SECRET_KEY, config.OKX_PASSPHRASE
    ]):
        print("❌ Live trading requires OKX API credentials in environment")
        sys.exit(1)
    
    system = HFTSystem(mode=args.mode)
    system.run()

if __name__ == "__main__":
    main()